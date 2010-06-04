import gobject

import dbus.exceptions

import cream.ipc

NAME = 'Notifications'
VENDOR = 'cream project'
VERSION = '0.1'

DEFAULT_EXPIRE_TIMEOUT = 10000

MAX_ID = 2**32 - 1

SERVICE_NAME = 'org.freedesktop.Notifications'
SERVICE_OBJECT = '/org/freedesktop/Notifications'

def generate_ids():
    """
        A generator for unique IDs.
    """
    while True:
        i = 1
        while i <= MAX_ID:
            yield i
            i += 1

class Capability(object):
    actions = 'actions'
    body = 'body'
    body_hyperlinks = 'body-hyperlinks'
    body_images = 'body-images'
    body_markup = 'body-markup'
    icon_multi = 'icon-multi'
    icon_static = 'icon-static'
    sound = 'sound'

class Urgency(object):
    low = 0
    normal = 1
    critical = 2

class Expires(object):
    default = -1
    never = 0

class Reason(object):
    expired = 1
    dismissed = 2
    closed = 3
    undefined = 4

class Notification(object):
    def __init__(self, id, app_name, replaces_id, app_icon, summary, body, actions, hints, expire_timeout):
        self.id = id
        self.app_name = app_name
        self.replaces_id = replaces_id
        self.app_icon = app_icon
        self.summary = summary
        self.body = body
        self.actions = actions
        self.hints = hints
        self.expire_timeout = expire_timeout

    def __repr__(self):
        return '<Notification object #%d at 0x%x (%r)>' % (self.id, id(self), str(self.summary))

class Server(cream.ipc.Object):
    __gsignals__ = {
        'get-capabilities': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_PYOBJECT, ()), # required to return an array of strings
        'show-notification': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,)),
        'hide-notification': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,)),
    }

    __ipc_signals__ = {
        'NotificationClosed': 'uu',
        'ActionInvoked': 'us',
    }

    def __init__(self):
        cream.ipc.Object.__init__(self,
            SERVICE_NAME,
            SERVICE_OBJECT
            )
        self.id_generator = generate_ids()
        self.notifications = {}

    def show(self, notification):
        self.notifications[notification.id] = notification
        print 'Show: %r' % notification
        self.emit('show-notification', notification)

    def hide(self, notification):
        del self.notifications[notification.id]
        print 'Hide: %r' % notification
        self.emit('hide-notification', notification)

    def close(self, notification, reason):
        self.hide(notification)
        self.emit_signal('NotificationClosed', notification.id, reason)

    def invoke_action(self, notification, action_key):
        self.emit_signal('ActionInvoked', notification.id, action_key)

    @cream.ipc.method('', 'as')
    def GetCapabilities(self):
        print ' --- get capabilities!'
        return self.emit('get-capabilities')

    @cream.ipc.method('u', '')
    def CloseNotification(self, id):
        if id in self.notifications:
            self.close(self.notifications[id], Reason.closed)
        else:
            raise DbusException()

    @cream.ipc.method('susssasa{sv}i', 'u')
    def Notify(self, app_name, replaces_id, app_icon, summary, body, actions, hints, expire_timeout):
        print 'Notification!'
        print ' - app name: %r' % app_name
        print ' - replaces id: %r' % replaces_id
        print ' - app icon: %r' % app_icon
        print ' - summary: %r' % summary
        print ' - body: %r' % body
        print ' - actions: %r' % actions
        print ' - hints: %r' % hints
        print ' - expire timeout: %r' % expire_timeout
        notification = Notification(self.id_generator.next(),
                                    app_name,
                                    replaces_id,
                                    app_icon,
                                    summary,
                                    body,
                                    actions,
                                    hints,
                                    expire_timeout)
        # setup expire timeout
        if expire_timeout == Expires.default:
            expire_timeout = DEFAULT_EXPIRE_TIMEOUT
        if expire_timeout != Expires.never:
            def _expire():
                self.close(notification, Reason.expired)
                return False
            gobject.timeout_add(expire_timeout, _expire)
        # showtime
        self.show(notification)
        return notification.id

    @cream.ipc.method('', 'sss')
    def GetServerInformation(self):
        return (NAME, VENDOR, VERSION)

if __name__ == '__main__':
    from dbus.mainloop.glib import DBusGMainLoop
    DBusGMainLoop(set_as_default=True)

    server = Server()

    import gobject
    mainloop = gobject.MainLoop()
    mainloop.run()

