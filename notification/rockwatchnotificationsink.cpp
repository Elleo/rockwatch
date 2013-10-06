#include <MApplication>
#include <QtDBus/QDBusConnection>
#include <QtDBus/QtDBus>
#include <QtDBus/QDBusMessage>
#include <notificationsystem/notificationsinkadaptor.h>
#include "rockwatchnotificationsink.h"

RockwatchNotificationSink::RockwatchNotificationSink(QObject *parent) : NotificationSink(parent) {
}

void RockwatchNotificationSink::addNotification(const Notification &notification) {
	const NotificationParameters& parameters = notification.parameters();
	QDBusInterface rockwatch("com.mikeasoft.rockwatch", "/rockwatch", "com.mikeasoft.rockwatch");
	if(parameters.value("eventType").toString() == "email.arrived") {
		rockwatch.call("showEmail", parameters.value("summary"), parameters.value("body"), " "); // Notification doesn't provide email message body, have to provide non-empty string for message to be displayed by Pebble
	} else {
		rockwatch.call("showSMS", parameters.value("summary"), parameters.value("body"));
	}
}

void RockwatchNotificationSink::removeNotification(uint notificationId) {
	Q_UNUSED(notificationId);
}

void RockwatchNotificationSink::addGroup(uint groupId, const NotificationParameters &parameters) {
	Q_UNUSED(groupId);
	Q_UNUSED(parameters);
}

void RockwatchNotificationSink::removeGroup(uint groupId) {
	Q_UNUSED(groupId);
}


int main(int argc, char *argv[]) {
	MApplication app(argc, argv);
	RockwatchNotificationSink *sink = new RockwatchNotificationSink(NULL);
	qDBusRegisterMetaType<Notification>();
	qDBusRegisterMetaType<NotificationGroup>();
	qDBusRegisterMetaType<NotificationParameters>();
	new NotificationSinkAdaptor(sink);
	QDBusConnection::sessionBus().registerService("com.mikeasoft.notificationsink");
	QDBusConnection::sessionBus().registerObject("/notificationsink", sink);

	return app.exec();
}
