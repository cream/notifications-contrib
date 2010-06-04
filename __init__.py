import gobject

import cream.ipc

MAX_ID = 2**32 - 1

SERVICE_NAME = 'org.freedesktop.Notifications'
SERVICE_OBJECT = '/org/freedesktop/Notifications'

def generate_ids():
    """
        A generator for unique IDs.
    """
    while True:
        i = 0
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

class Server(cream.ipc.Object):
    __gsignals__ = {
        'get-capabilities': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_PYOBJECT, ()), # required to return an array of strings
    }

    def __init__(self):
        cream.ipc.Object.__init__(self,
            SERVICE_NAME,
            SERVICE_OBJECT
            )
        self.id_generator = generate_ids()

    @cream.ipc.method('', 'as')
    def GetCapabilities(self):
        print ' --- get capabilities!'
        return self.emit('get-capabilities')

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
        return notification.id

if __name__ == '__main__':
    from dbus.mainloop.glib import DBusGMainLoop
    DBusGMainLoop(set_as_default=True)

    server = Server()

    import gobject
    mainloop = gobject.MainLoop()
    mainloop.run()

