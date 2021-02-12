from fsgamesys.options.option import Option
from launcher.i18n import gettext
from launcher.system.prefs.baseprefspanel import BasePrefsPanel
from launcher.system.prefs.baseprefswindow import BasePrefsWindow


class NetPlayPrefsWindow(BasePrefsWindow):
    def __init__(self, parent):
        super().__init__(parent, title=gettext("Net play preferences"))
        self.panel = NetPlayPrefsPanel(self)
        self.layout.add(self.panel, fill=True, expand=True)


class NetPlayPrefsPanel(BasePrefsPanel):
    def __init__(self, parent):
        super().__init__(parent)
        # FIXME
        self.set_min_size((540, 100))
        self.layout.set_padding(20, 0, 20, 20)

        self.add_option(Option.IRC_NICK)
        self.add_option(Option.NETPLAY_TAG)
        self.add_option(Option.IRC_SERVER)
