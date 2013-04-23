#!/usr/bin/env python
from QtMobility.Messaging import *
from PySide.QtCore import *
import sys
import pebble
import dbus, dbus.glib


class RockWatch(QObject):


	def __init__(self):
		QObject.__init__(self)
		self.pebbleId = "00:18:33:AC:95:2D"
#		self.messageManager = QMessageManager()
#		self.messageManager.registerNotificationFilter(QMessageFilter.byStatus(QMessage.Incoming))
		self.lastCheck = QDateTime()
		self.stopped = True
		self.paused = False
		self.artist = "Unknown Artist"
		self.album = "Unknown Album"
		self.track = "Unknown Track"


	def connect(self):
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
#		self.messageManager.messageAdded.connect(self.showNewMessage)


	def metadataChanged(self, key, val, *args):
		if key == "artist":
			self.artist = str(val[0])
		elif key == "album":
			self.album = str(val[0])
		elif key == "title":
			self.track = str(val[0])
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


	def showNewMessage(self, msgId=None, messageFilter=None):
		print self
		print msgId
		if msgId == None:
			# HACK: python wrapper for QtMobility.Messaging is buggy and doesn"t send msgIds
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


	def quit(self):
		self.pebble.disconnect()


if __name__ == "__main__":
	app = QCoreApplication(sys.argv)
	r = RockWatch()
	r.connect()
	app.exec_()
