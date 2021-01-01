from launcher.i18n import gettext
from launcher.settings.keyboard_settings_page import KeyboardSettingsPage
from launcher.system.prefs.baseprefswindow import BasePrefsWindow


class KeyboardPrefsWindow(BasePrefsWindow):
    def __init__(self, parent):
        super().__init__(parent, title=gettext("Keyboard preferences"))
        self.panel = KeyboardSettingsPage(self)
        self.layout.add(self.panel, fill=True, expand=True)
