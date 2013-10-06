TEMPLATE = app
QT += network
QT += dbus
CONFIG += meegotouch
TARGET = "rockwatchnotification"
DEPENDPATH += .
INCLUDEPATH += .
INCLUDEPATH += /usr/include/resource/qt4

LIBS += -lssl
LIBS += -lresourceqt
LIBS += -lnotificationsystem

# Input
HEADERS += \
    rockwatchnotificationsink.h \
    mnotificationmanagerinterface.h
SOURCES += rockwatchnotificationsink.cpp \
    mnotificationmanagerinterface.cpp
#FORMS#

PREFIX = /opt/rockwatch

#MAKE INSTALL

INSTALLS += target
  target.path = $$PREFIX
