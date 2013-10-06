TEMPLATE = subdirs
SUBDIRS  = notification

#install
rockwatch.path = /opt/rockwatch/
rockwatch.files = *.py *.sh

pebble.path = /opt/rockwatch/pebble/
pebble.files = pebble/*

deps.path = /opt/rockwatch/deps
deps.files = deps/*

images.path = /opt/rockwatch/
images.files = *.png

desktop.path = /usr/share/applications/
desktop.files = rockwatch.desktop

qml.path = /opt/rockwatch/qml/
qml.files = qml/*

services.path = /usr/share/dbus-1/services
services.files = *.service

INSTALLS += rockwatch notificationsink pebble deps images desktop qml services
