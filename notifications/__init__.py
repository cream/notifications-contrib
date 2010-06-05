import cream.ipc

from .spec import Server

FRONTEND_MANAGER_SERVICE_NAME = 'org.cream.notifications.FrontendManager'
FRONTEND_MANAGER_SERVICE_OBJECT = '/org/cream/notifications/FrontendManager'

NOTIFICATION_CODE = 'ususssasa{sv}i'

def notification_to_dbus(n):
    return (n.id,
            n.app_name,
            n.replaces_id,
            n.app_icon,
            n.summary,
            n.body,
            n.action_array,
            n.hints,
            n.expires_timeout)


class FrontendManager(cream.ipc.Object):
    __ipc_signals__ = {
        'show_notification': NOTIFICATION_CODE,
        'hide_notification': NOTIFICATION_CODE,
    }

    def __init__(self):
        cream.ipc.Object.__init__(self,
                FRONTEND_MANAGER_SERVICE_NAME,
                FRONTEND_MANAGER_SERVICE_OBJECT
                )

        self.server = Server()
        self.server.connect('get-capabilities', self.sig_get_capabilities)
        self.server.connect('show-notification', self.sig_show_notification)
        self.server.connect('hide-notification', self.sig_hide_notification)

        self.frontends = {} # bus name: capabilities

    def sig_get_capabilities(self, server):
        """
            Return ALL capabilities.
        """
        all_caps = set()
        for caps in self.frontends.itervalues():
            all_caps.add(caps)
        return list(all_caps)

    def sig_show_notification(self, server, notification):
        self.emit_signal('show_notification', *notification_to_dbus(notification))

    def sig_hide_notification(self, server, notification):
        self.emit_signal('hide_notification', *notification_to_dbus(notification))

    @cream.ipc.method('sas', '')
    def register(self, bus_name, capabilities):
        self.frontends[str(bus_name)] = list(capabilities)

