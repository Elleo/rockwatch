#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2013 Mike Sheldon <elleo@gnu.org>
# 
# This program is free software: you can redistribute it and/or modify 
# it under the terms of the GNU General Public License as published by 
# the Free Software Foundation, either version 3 of the License, or 
# (at your option) any later version. 
# 
# This program is distributed in the hope that it will be useful, 
# but WITHOUT ANY WARRANTY; without even the implied warranty of 
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the 
# GNU General Public License for more details. 
# 
# You should have received a copy of the GNU General Public License 
# along with this program. If not, see <http://www.gnu.org/licenses/>.

from PySide.QtCore import *
from PySide.QtDeclarative import *
from PySide.QtGui import *
import sys, signal, threading, urlparse, json
import urllib2, tempfile, hashlib, StringIO, traceback
import dbus, dbus.glib, dbus.service
from pebble import Pebble, PebbleError
from pebble.pebble import PebbleBundle
from pebble.LightBluePebble import LightBluePebbleError
from AppListModel import *


FIRMWARE_URL = "http://pebblefw.s3.amazonaws.com/pebble/ev2_4/release/latest.json"


class Signals(QObject):


	onDoneWorking = Signal()
	onConnect = Signal()
	onConnected = Signal()
	onNewFirmwareAvailable = Signal(str, str)
	onMessage = Signal(str, str)
	
	
	def __init__(self, parent = None):
		super(Signals, self).__init__(parent)


class Rockwatch(dbus.service.Object):


	def __init__(self, parent = None):
		super(Rockwatch, self).__init__(parent)
		self.app = QApplication(sys.argv)
		self.app.setApplicationName("Rockwatch")
		self.pebble = None
		self.signals = Signals()
		self.lastCheck = QDateTime()
		self.stopped = True
		self.paused = False
		self.connecting = False
		self.firmwareUpdated = False
		self.artist = "Unknown Artist"
		self.album = "Unknown Album"
		self.track = "Unknown Track"
		self.view = QDeclarativeView()
		self.view.setSource("/opt/rockwatch/qml/Main.qml")
		self.rootObject = self.view.rootObject()
		self.rootObject.openFile("Menu.qml")
		self.rootObject.quit.connect(self.quit)
		self.rootObject.ping.connect(self.ping)
		self.rootObject.firmwareCheck.connect(self.firmwareCheck)
		self.rootObject.upgradeFirmware.connect(self.upgradeFirmware)
		self.rootObject.watchfaceSelected.connect(self.installApp)
		self.rootObject.getAppList.connect(self.getAppList)
		self.rootObject.deleteApp.connect(self.deleteApp)
		self.appListModel = AppListModel()
		self.context = self.view.rootContext()
		self.context.setContextProperty('appListModel', self.appListModel)
		self.signals.onDoneWorking.connect(self.doneWorking)
		self.signals.onConnect.connect(self.connect)
		self.signals.onConnected.connect(self.connected)
		self.signals.onMessage.connect(self.message)
		self.signals.onNewFirmwareAvailable.connect(self.newFirmwareAvailable)
		self.view.showFullScreen()
		self.mutex = threading.Lock()
		self.timer = QTimer(self.app)
		self.app.connect(self.timer, SIGNAL("timeout()"), self.checkConnection)
		self.timer.start(30000)
		QTimer.singleShot(0, self.findPebble)
		sys.exit(self.app.exec_())


	def findPebble(self):
		self.connecting = True
		sysbus = dbus.SystemBus()
		manager = dbus.Interface(sysbus.get_object('org.bluez', '/'), 'org.bluez.Manager')
		adapterPath = manager.DefaultAdapter()
		adapter = dbus.Interface(sysbus.get_object('org.bluez', adapterPath), 'org.bluez.Adapter')
		self.pebbleId = None
		for devicePath in adapter.ListDevices():
			device = dbus.Interface(sysbus.get_object('org.bluez', devicePath),'org.bluez.Device')
			deviceProperties = device.GetProperties()
			name = deviceProperties['Name']
			if name.lower()[:6] == "pebble":
				self.pebbleId = deviceProperties['Address']
				self.connect()
				break
		if self.pebbleId == None:
			self.connecting = False
			self.message("Couldn't find Pebble", "Sorry! I couldn't find your Pebble. Please ensure that it has been paired with your N9 and that its name begins with 'Pebble'", True)


	def doneWorking(self):
		self.rootObject.stopWorking()


	def message(self, title, message, quitAfter = False):
		self.rootObject.showMessage(title, message, quitAfter)

	
	def connect(self):
		self.rootObject.startWorking()
		thread = threading.Thread(target=self._connect)
		thread.start()


	def checkConnection(self):
		self.mutex.acquire()
		if not self.pebble or not self.pebble.is_alive():
			if self.connecting and not self.firmwareUpdated:
				self.signals.onMessage.emit("Unable to connect to Pebble", "Check that your phone's bluetooth is switched on and that your Pebble is nearby.")
			self.findPebble() # Try to reconnect
		self.mutex.release()


	def _connect(self):
		self.connecting = True
		try:
			self.pebble = Pebble(self.pebbleId, True, False)
			self.pebble.register_endpoint("MUSIC_CONTROL", self.musicControl)
		except LightBluePebbleError, e:
			self.signals.onMessage.emit("Unable to connect to Pebble", str(e))
			self.connecting = False
			return
		dbus_main_loop = dbus.glib.DBusGMainLoop(set_as_default=True)
		self.bus = dbus.SessionBus(dbus_main_loop)
		# Setup our own DBUS service
		bus_name = dbus.service.BusName("com.mikeasoft.rockwatch", bus=self.bus)
		dbus.service.Object.__init__(self, object_path="/rockwatch", bus_name=bus_name)

		# If MeeGo multimedia framework has already been started,
		# we need to connect to it
		self.mafwIfaceChanged()

		self.bus.add_signal_receiver(self.mafwIfaceChanged, dbus_interface="org.freedesktop.DBus", signal_name="NameOwnerChanged", arg0=self.MAFW_GST_RENDERER)
		self.bus.add_signal_receiver(self.metadataChanged, dbus_interface="com.nokia.mafw.renderer", signal_name="metadata_changed")
		self.bus.add_signal_receiver(self.stateChanged, dbus_interface="com.nokia.mafw.renderer", signal_name="state_changed")

		self.firmwareUpdated = False
		self.signals.onConnected.emit()


	def connected(self):
		self.connecting = False
		self.doneWorking()
		self.rootObject.connected()


	@dbus.service.method("com.mikeasoft.rockwatch")
	def ping(self):
		try:
			if not self.pebble.is_alive() and not self.connecting:
				self.findPebble()
				if self.pebbleId == None:
					return
			self.pebble.ping()
		except PebbleError, e:
			self.signals.onMessage.emit("Unable to ping Pebble", str(e))


	@dbus.service.method("com.mikeasoft.rockwatch")
	def nowPlaying(self, artist, album, title):
		self.metadataChanged("artist", [artist])
		self.metadataChanged("album", [album])
		self.metadataChanged("title", [title])

	mafwIface = property(lambda self: getattr(self, '_mafwIface', None))
	MAFW_GST_RENDERER = "com.nokia.mafw.renderer.MafwGstRendererPlugin.mafw_gst_renderer"

	def mafwIfaceChanged(self, *args):
		''' Our previous mafwIface may be no longer valid '''
		try:
			mafwProxy = self.bus.get_object(
				self.MAFW_GST_RENDERER,
				"/com/nokia/mafw/renderer/mafw_gst_renderer"
			)
			self._mafwIface = dbus.Interface(
				mafwProxy, dbus_interface="com.nokia.mafw.renderer"
			)
			status = self.mafwIface.get_status()
		except Exception:
			self._mafwIface = None
		else:
			if status[2] == 0:
				self.stopped = True
				self.paused = False
			elif status[2] == 1:
				self.paused = False
				self.stopped = False
			elif status[2] == 2:
				self.paused = True
				self.stopped = False

	def metadataChanged(self, key, val, *args):
		if key == "artist":
			self.artist = unicode(val[0]).encode('ascii', 'ignore')
		elif key == "album":
			self.album = unicode(val[0]).encode('ascii', 'ignore')
		elif key == "title":
			self.track = unicode(val[0]).encode('ascii', 'ignore')
		try:
			self.mutex.acquire()
			if not self.connecting:
				if not self.pebble.is_alive():
					return
				self.pebble.set_nowplaying_metadata(self.track, self.album, self.artist)
			self.mutex.release()
		except PebbleError, e:
			self.signals.onMessage.emit("Unable to update music information", str(e))


	def stateChanged(self, state):
		if state == 0:
			self.paused = False
			self.stopped = True
		elif state == 1:
			self.paused = False
			self.stopped = False
		elif state == 2:
			self.paused = True


	def musicControl(self, endpoint, data):
		mafwIface = self.mafwIface
		if not mafwIface:
			return

		if data == "NEXT":
			mafwIface.next()
		elif data == "PREVIOUS":
			mafwIface.previous()
		elif data == "PLAYPAUSE":
			if self.stopped:
				mafwIface.play()
				self.stopped = False
				self.paused = False
			elif not self.paused:
				mafwIface.pause()
				self.paused = True
				self.stopped = False
			else:
				mafwIface.resume()
				self.paused = False
				self.stopped = False


	def messageReceived(self, data):
		message = data[1]['content'].title()
		sender = data[0]['sms-service-centre'].title()
		self.showSMS(sender, message)


	@dbus.service.method("com.mikeasoft.rockwatch")
	def showSMS(self, sender, message):
		sender = unicode(sender).encode('ascii', 'ignore')
		message = unicode(message).encode('ascii', 'ignore')
		try:
			if not self.pebble.is_alive() and not self.connecting:
				self.findPebble()
				if self.pebbleId == None:
					return
			self.pebble.notification_sms(sender, message)
		except PebbleError, e:
			self.signals.onMessage.emit("Unable to send SMS notification", str(e))


	@dbus.service.method("com.mikeasoft.rockwatch")
	def showEmail(self, sender, subject, body):
		sender = unicode(sender).encode('ascii', 'ignore')
		subject = unicode(subject).encode('ascii', 'ignore')
		body = unicode(body).encode('ascii', 'ignore')
		try:
			if not self.pebble.is_alive() and not self.connecting:
				self.findPebble()
				if self.pebbleId == None:
					return
			self.pebble.notification_email(sender, subject, body)
		except PebbleError, e:
			self.signals.onMessage.emit("Unable to send e-mail notification", str(e))


	@dbus.service.method("com.mikeasoft.rockwatch")
	def installApp(self, appUri):
		if not self.pebble.is_alive() and not self.connecting:
			self.findPebble()
			if self.pebbleId == None:
				return
		self.rootObject.startWorking()
		thread = threading.Thread(target=self._installApp, args=(appUri,))
		thread.start()
		

	def _installApp(self, appUri):
		app = urlparse.urlparse(appUri).path
		try:
			# Check to see if this app is already installed
			bundle = PebbleBundle(app)
			if not bundle.is_app_bundle():
				self.signals.onMessage.emit("Unable to install app", "This does not appear to be a valid Pebble application package.")
				self.signals.onDoneWorking.emit()
				return
			appMetadata = bundle.get_app_metadata()
			appName = appMetadata['app_name']
			installedApps = self.pebble.get_appbank_status()
			alreadyInstalled = False
			if installedApps:
				for appDetails in installedApps['apps']:
					if appDetails['name'] == appName:
						alreadyInstalled = True
			if alreadyInstalled:
				self.pebble.reinstall_app(app)
			else:
				self.pebble.install_app(app)
		except PebbleError, e:
			self.signals.onMessage.emit("Unable to install app", str(e))
		self.signals.onDoneWorking.emit()


	@dbus.service.method("com.mikeasoft.rockwatch")
	def listApps(self):
		try:
			if not self.pebble.is_alive() and not self.connecting:
				self.findPebble()
				if self.pebbleId == None:
					return
			apps = self.pebble.get_appbank_status()
		except PebbleError, e:
			self.signals.onMessage.emit("Unable to retrieve app list", str(e))
			return

		return apps


	def getAppList(self):
		self.appListModel.clear()
		apps = self.listApps()
		if apps:
			for appDetails in apps['apps']:
				app = App(appDetails['id'], appDetails['name'], appDetails['company'], appDetails['index'])
				self.appListModel.addToEnd(app)


	@dbus.service.method("com.mikeasoft.rockwatch")
	def deleteApp(self, appId, appIndex):
		if not self.pebble.is_alive() and not self.connecting:
			self.findPebble()
			if self.pebbleId == None:
				return
		self.rootObject.startWorking()
		thread = threading.Thread(target=self._deleteApp, args=(appId, appIndex))
		thread.start()


	def _deleteApp(self, appId, appIndex):
		try:
			self.pebble.remove_app(appId, appIndex)
		except PebbleError, e:
			self.signals.onMessage.emit("Unable to remove app", str(e))
		self.signals.onDoneWorking.emit()
		self.getAppList()


	def firmwareCheck(self):
		if not self.pebble.is_alive() and not self.connecting:
			self.findPebble()
			if self.pebbleId == None:
				return
		self.rootObject.startWorking()
		thread = threading.Thread(target=self._firmwareCheck)
		thread.start()

	
	def _firmwareCheck(self):
		try:
			firmwareMetadata = json.load(urllib2.urlopen(FIRMWARE_URL))
			versionData = self.pebble.get_versions()
			currentTimestamp = int(versionData['normal_fw']['timestamp'])
			latestTimestamp = int(firmwareMetadata['normal']['timestamp'])
			if latestTimestamp > currentTimestamp:
				self.signals.onNewFirmwareAvailable.emit(versionData['normal_fw']['version'], firmwareMetadata['normal']['friendlyVersion'])
			else:
				self.signals.onMessage.emit("Up-to-date", "Your Pebble is running the latest firmware.")
		except Exception, e:
			self.signals.onMessage.emit("Unable to fetch firmware information", str(e))
		self.signals.onDoneWorking.emit()


	def newFirmwareAvailable(self, oldVersion, newVersion):
		self.rootObject.newFirmwareAvailable(oldVersion, newVersion)


	def upgradeFirmware(self):
		if not self.pebble.is_alive() and not self.connecting:
			self.findPebble()
			if self.pebbleId == None:
				return
		self.rootObject.startWorking()
		thread = threading.Thread(target=self._upgradeFirmware)
		thread.start()


	def _upgradeFirmware(self):
		try:
			firmwareMetadata = json.load(urllib2.urlopen(FIRMWARE_URL))
			firmwareBundleUrl = firmwareMetadata['normal']['url']

			firmwareData = StringIO.StringIO(urllib2.urlopen(firmwareBundleUrl).read())
			fileHash = hashlib.sha256(firmwareData.read())
			firmwareData.seek(0)
			if fileHash.hexdigest() != firmwareMetadata['normal']['sha-256']:
				self.signals.onMessage.emit("Firmware upgrade failed", "The firmware file doesn't appear to have downloaded correctly. Please try again.")
			else:
				self.pebble.install_firmware(firmwareData)
				self.pebble.reset()
				self.firmwareUpdated = True
				self.signals.onMessage.emit("Firmware upgrade", "Your Pebble's firmware has now been upgraded to the latest version")
				self.signals.onConnect.emit()
			firmwareData.close()
		except Exception, e:
			self.signals.onMessage.emit("Firmware upgrade failed", str(e))
			traceback.print_exc()
		self.signals.onDoneWorking.emit()


	def quit(self):
		sys.exit()


if __name__ == "__main__":
	signal.signal(signal.SIGINT, signal.SIG_DFL)
	r = Rockwatch()
