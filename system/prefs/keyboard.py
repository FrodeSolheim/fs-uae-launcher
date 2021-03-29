from launcher.i18n import gettext
from launcher.settings.keyboard_settings_page import KeyboardSettingsPage
from system.classes.shellobject import shellObject
from system.classes.windowcache import WindowCache
from system.prefs.components.baseprefswindow import BasePrefsWindow


@shellObject
class Keyboard:
    @staticmethod
    def open(**kwargs):
        WindowCache.open(KeyboardPrefsWindow, **kwargs)


class KeyboardPrefsWindow(BasePrefsWindow):
    def __init__(self, parent=None):
        super().__init__(parent, title=gettext("Keyboard preferences"))
        self.panel = KeyboardSettingsPage(self)
        self.layout.add(self.panel, fill=True, expand=True)
