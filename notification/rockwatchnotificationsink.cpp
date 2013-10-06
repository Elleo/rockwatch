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
	QString summary = parameters.value("summary").toString();
	QString body = parameters.value("body").toString();
	// Pebble won't display notifications containing empty strings in either
	// component, so we replace them with a single space character.
	// But only replace one or the other, since there's no point displaying
	// completely empty notifications.
	if(summary.length() == 0) {
		summary = " ";
	}else if(body.length() == 0) {
		body = " ";
	}
	if(parameters.value("eventType").toString() == "email.arrived") {
		rockwatch.call("showEmail", summary, body, " "); // Notification doesn't provide email message body
	} else {
		rockwatch.call("showSMS", summary, body);
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
