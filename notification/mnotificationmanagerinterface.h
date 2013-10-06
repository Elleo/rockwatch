/*
 * This file was generated by qdbusxml2cpp version 0.7
 * Command line was: qdbusxml2cpp -N -p - dbusinterfacenotificationsink.xml
 *
 * qdbusxml2cpp is Copyright (C) 2011 Nokia Corporation and/or its subsidiary(-ies).
 *
 * This is an auto-generated file.
 * Do not edit! All changes made to it will be lost.
 */

#ifndef QDBUSXML2CPP_PROXY_1316370481
#define QDBUSXML2CPP_PROXY_1316370481

#include <QtCore/QObject>
#include <QtCore/QByteArray>
#include <QtCore/QList>
#include <QtCore/QMap>
#include <QtCore/QString>
#include <QtCore/QStringList>
#include <QtCore/QVariant>
#include <QtDBus/QtDBus>

/*
 * Proxy class for interface com.meego.core.MNotificationManager
 */
class MNotificationManagerInterface: public QDBusAbstractInterface
{
    Q_OBJECT
public:
    static inline const char *staticInterfaceName()
    { return "com.meego.core.MNotificationManager"; }

public:
    MNotificationManagerInterface(const QString &service, const QString &path, const QDBusConnection &connection, QObject *parent = 0);

    ~MNotificationManagerInterface();

public Q_SLOTS: // METHODS
    inline QDBusPendingReply<> registerSink(const QString &service, const QString &path)
    {
        QList<QVariant> argumentList;
        argumentList << qVariantFromValue(service) << qVariantFromValue(path);
        return asyncCallWithArgumentList(QLatin1String("registerSink"), argumentList);
    }

    inline QDBusPendingReply<> unregisterSink(const QString &service, const QString &path)
    {
        QList<QVariant> argumentList;
        argumentList << qVariantFromValue(service) << qVariantFromValue(path);
        return asyncCallWithArgumentList(QLatin1String("unregisterSink"), argumentList);
    }

Q_SIGNALS: // SIGNALS
};

#endif
