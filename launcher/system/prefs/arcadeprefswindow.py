from launcher.i18n import gettext
from launcher.settings.arcade_settings_page import ArcadeSettingsPage
from launcher.system.prefs.common.baseprefswindow import BasePrefsWindow


class ArcadePrefsWindow(BasePrefsWindow):
    def __init__(self, parent):
        super().__init__(parent, title=gettext("Arcade preferences"))
        self.panel = ArcadeSettingsPage(self)
        self.layout.add(self.panel, fill=True, expand=True)
