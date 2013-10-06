#ifndef ROCKWATCHNOTIFICATIONSINK_H
#define ROCKWATCHNOTIFICATIONSINK_H

#include <QtCore/QMap>
#include <notificationsystem/notificationsink.h>
#include <notificationsystem/notification.h>
#include <notificationsystem/notificationgroup.h>
#include "mnotificationmanagerinterface.h"

class RockwatchNotificationSink : public NotificationSink
{
	Q_OBJECT
public:
	explicit RockwatchNotificationSink(QObject *parent);

public slots:
	void addNotification(const Notification &notification);
	void removeNotification(uint notificationId);
	void addGroup(uint groupId, const NotificationParameters &parameters);
	void removeGroup(uint groupId);
};

#endif

