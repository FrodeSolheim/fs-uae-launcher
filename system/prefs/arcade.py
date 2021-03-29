from launcher.i18n import gettext
from launcher.settings.arcade_settings_page import ArcadeSettingsPage
from system.classes.shellobject import shellObject
from system.classes.windowcache import WindowCache
from system.prefs.components.baseprefswindow import BasePrefsWindow


@shellObject
class Arcade:
    @staticmethod
    def open(**kwargs):
        WindowCache.open(ArcadePrefsWindow, **kwargs)


class ArcadePrefsWindow(BasePrefsWindow):
    def __init__(self, parent=None):
        super().__init__(parent, title=gettext("Arcade preferences"))
        self.panel = ArcadeSettingsPage(self)
        self.layout.add(self.panel, fill=True, expand=True)
