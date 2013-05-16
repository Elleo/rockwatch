#!/usr/bin/env python
from QtMobility.Messaging import *
from QtMobility.Connectivity import *
from PySide.QtCore import *
from PySide.QtDeclarative import *
from PySide.QtGui import *
import sys, signal, threading, urlparse
import dbus, dbus.glib
import pebble


class Signals(QObject):


	onDoneWorking = Signal()
	onConnected = Signal()
	onError = Signal(str, str)
	
	
	def __init__(self, parent = None):
		super(Signals, self).__init__(parent)


class Rockwatch(QObject):


	def __init__(self, parent = None):
		super(Rockwatch, self).__init__(parent)
		self.app = QApplication(sys.argv)
		self.app.setApplicationName("Rockwatch")
		self.signals = Signals()
#		self.messageManager = QMessageManager()
#		self.messageManager.registerNotificationFilter(QMessageFilter.byStatus(QMessage.Incoming))
		self.lastCheck = QDateTime()
		self.stopped = True
		self.paused = False
		self.artist = "Unknown Artist"
		self.album = "Unknown Album"
		self.track = "Unknown Track"
		self.view = QDeclarativeView()
		self.view.setSource("/home/developer/rockwatch/qml/Main.qml")
		self.rootObject = self.view.rootObject()
		self.rootObject.openFile("/home/developer/rockwatch/qml/Menu.qml")
		self.rootObject.quit.connect(self.quit)
		self.rootObject.ping.connect(self.ping)
		self.rootObject.watchfaceSelected.connect(self.installApp)
		self.context = self.view.rootContext()
		self.signals.onDoneWorking.connect(self.doneWorking)
		self.signals.onConnected.connect(self.connected)
		self.signals.onError.connect(self.error)
		self.view.showFullScreen()
		self.findPebble()
		sys.exit(self.app.exec_())


	def findPebble(self):
		sysbus = dbus.SystemBus()
		manager = dbus.Interface(sysbus.get_object('org.bluez', '/'), 'org.bluez.Manager')
		adapterPath = manager.DefaultAdapter()
		adapter = dbus.Interface(sysbus.get_object('org.bluez', adapterPath), 'org.bluez.Adapter')
		for devicePath in adapter.ListDevices():
			device = dbus.Interface(sysbus.get_object('org.bluez', devicePath),'org.bluez.Device')
			deviceProperties = device.GetProperties()
			name = deviceProperties['Name']
			if name.lower()[:6] == "pebble":
				self.pebbleId = deviceProperties['Address']
				QTimer.singleShot(0, self.connect)
				break
		if self.pebbleId == None:
			self.error("Couldn't find Pebble", "Sorry! I couldn't find your Pebble. Please ensure that it has been paired with your N9 and that its name begins with 'Pebble'", True)


	def doneWorking(self):
		self.rootObject.stopWorking()


	def error(self, title, message, quitAfter = False):
		self.rootObject.showMessage(title, message, quitAfter)

	
	def connect(self):
		self.rootObject.startWorking()
		thread = threading.Thread(target=self._connect)
		thread.start()


	def _connect(self):
		self.pebble = pebble.Pebble(self.pebbleId, True, False)
		self.pebble.register_endpoint("MUSIC_CONTROL", self.musicControl)
		dbus_main_loop = dbus.glib.DBusGMainLoop(set_as_default=True)
		self.bus = dbus.SessionBus(dbus_main_loop)
		self.mafwProxy = self.bus.get_object("com.nokia.mafw.renderer.MafwGstRendererPlugin.mafw_gst_renderer",
		                       "/com/nokia/mafw/renderer/mafw_gst_renderer")
		self.mafwIface = dbus.Interface(self.mafwProxy, dbus_interface="com.nokia.mafw.renderer")
		status = self.mafwIface.get_status()
		if status[2] == 0:
			self.stopped = True
			self.paused = False
		elif status[2] == 1:
			self.paused = False
			self.stopped = False
		elif status[2] == 2:
			self.paused = True
			self.stopped = False
		self.bus.add_signal_receiver(self.metadataChanged, dbus_interface="com.nokia.mafw.renderer", signal_name="metadata_changed")
		self.bus.add_signal_receiver(self.stateChanged, dbus_interface="com.nokia.mafw.renderer", signal_name="state_changed")
		sms = self.bus.get_object('org.freedesktop.Telepathy.ConnectionManager.ring', '/org/freedesktop/Telepathy/Connection/ring/tel/ring/text13')
		self.smsFace = dbus.Interface(sms, 'org.freedesktop.Telepathy.Channel.Interface.Messages')
		self.bus.add_signal_receiver(self.messageReceived, dbus_interface="org.freedesktop.Telepathy.Channel.Interface.Messages", signal_name="MessageReceived")
#		self.messageManager.messageAdded.connect(self.showNewMessage)
		self.signals.onConnected.emit()


	def connected(self):
		self.doneWorking()
		self.rootObject.connected()


	def ping(self):
		self.pebble.ping()


	def metadataChanged(self, key, val, *args):
		if key == "artist":
			self.artist = unicode(val[0]).encode('ascii', 'ignore')
		elif key == "album":
			self.album = unicode(val[0]).encode('ascii', 'ignore')
		elif key == "title":
			self.track = unicode(val[0]).encode('ascii', 'ignore')
		self.pebble.set_nowplaying_metadata(self.track, self.album, self.artist)


	def stateChanged(self, state):
		print state
		if state == 0:
			self.paused = False
			self.stopped = True
		elif state == 1:
			self.paused = False
			self.stopped = False
		elif state == 2:
			self.paused = True


	def musicControl(self, endpoint, data):
		print endpoint, data
		if data == "NEXT":
			self.mafwIface.next()
		elif data == "PREVIOUS":
			self.mafwIface.previous()
		elif data == "PLAYPAUSE":
			if self.stopped:
				print "Playing"
				self.mafwIface.play()
				self.stopped = False
				self.paused = False
			elif not self.paused:
				print "Pausing"
				self.mafwIface.pause()
				self.paused = False
				self.stopped = False
			else:
				print "Resuming"
				self.mafwIface.resume()
				self.paused = True
				self.stopped = False


	def messageReceived(self, data):
		print data
		message = unicode(data[1]['content'].title()).encode('ascii', 'ignore')
		print message
		sender = unicode(data[0]['sms-service-centre'].title()).encode('ascii', 'ignore')
		print sender
		self.pebble.notification_sms(sender, message)


	def showNewMessage(self, msgId=None, messageFilter=None):
		print self
		print msgId
		if msgId == None:
			# HACK: python wrapper for QtMobility.Messaging is buggy and doesn't send msgIds
			#sortOrder = QMessageSortOrder.byReceptionTimeStamp(Qt.DescendingOrder)
			self.lastCheck = QDateTime()
			self.messageFilter = QMessageFilter.byReceptionTimeStamp(self.lastCheck, QMessageDataComparator.GreaterThanEqual)
			matchingIds = self.messageManager.queryMessages(self.messageFilter)
		else:
			matchingIds = [msgId]
		for msgId in matchingIds:
			message = self.messageManager.message(msgId)
			if self.messageManager.error() == QMessageManager.NoError:
				print message.from_().addressee(), message.subject()
				if message.type() == QMessage.Sms:
					self.pebble.notification_sms(message.from_().addressee(), message.find(message.bodyId()).textContent())
				else:
					self.pebble.notification_email(message.from_().addressee(), message.subject(), message.find(message.bodyId()).textContent())


	def installApp(self, appUri):
		self.rootObject.startWorking()
		thread = threading.Thread(target=self._installApp, args=(appUri,))
		thread.start()
		

	def _installApp(self, appUri):
		app = urlparse.urlparse(appUri).path
		self.pebble.install_app(app)
		self.signals.onDoneWorking.emit()


	def quit(self):
		sys.exit()


if __name__ == "__main__":
	signal.signal(signal.SIGINT, signal.SIG_DFL)
	r = Rockwatch()
