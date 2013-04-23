TEMPLATE = lib
DEPENDPATH += . 

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

INSTALLS += rockwatch pebble deps images desktop qml
