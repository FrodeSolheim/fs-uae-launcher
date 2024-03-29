from typing import Optional

from fsgamesys.options.option import Option
from fswidgets.widget import Widget
from launcher.i18n import gettext
from system.classes.shellobject import shellObject
from system.classes.windowcache import WindowCache
from system.prefs.components.baseprefspanel import BasePrefsPanel
from system.prefs.components.baseprefswindow import BasePrefsWindow


@shellObject
class NetPlay:
    @staticmethod
    def open(**kwargs):
        WindowCache.open(NetPlayPrefsWindow, **kwargs)


class NetPlayPrefsWindow(BasePrefsWindow):
    def __init__(self, parent: Optional[Widget] = None):
        super().__init__(parent, title=gettext("Net play preferences"))
        self.panel = NetPlayPrefsPanel(self)
        self.layout.add(self.panel, fill=True, expand=True)


class NetPlayPrefsPanel(BasePrefsPanel):
    def __init__(self, parent: Widget):
        super().__init__(parent)
        # FIXME
        self.set_min_size((540, 100))
        self.layout.set_padding(20, 0, 20, 20)

        self.add_option(Option.IRC_NICK)
        self.add_option(Option.NETPLAY_TAG)
        self.add_option(Option.IRC_SERVER)
