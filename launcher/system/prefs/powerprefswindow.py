from fsgs.options.option import Option
from launcher.i18n import gettext
from launcher.system.prefs.baseprefspanel import BasePrefsPanel
from launcher.system.prefs.baseprefswindow import BasePrefsWindow


class PowerPrefsWindow(BasePrefsWindow):
    def __init__(self, parent):
        super().__init__(parent, title=gettext("Power preferences"))
        self.panel = PowerPrefsPanel(self)
        self.layout.add(self.panel, fill=True, expand=True)


class PowerPrefsPanel(BasePrefsPanel):
    def __init__(self, parent):
        super().__init__(parent)
        # FIXME
        self.set_min_size((540, 100))
        self.layout.set_padding(10, 20, 10, 20, css=True)

        # if linux:
        self.add_section("Linux", margin_top=10)
        self.add_option(Option.GAME_MODE)
        self.add_option(Option.GOVERNOR_WARNING)
