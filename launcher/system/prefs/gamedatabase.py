from launcher.i18n import gettext
from launcher.settings.gamedatabasesettingspage import GameDatabaseSettingsPage
from launcher.system.classes.shellobject import shellObject
from launcher.system.classes.windowcache import WindowCache
from launcher.system.prefs.components.baseprefswindow import BasePrefsWindow


@shellObject
class GameDatabase:
    @staticmethod
    def open(**kwargs):
        WindowCache.open(GameDatabasePrefsWindow, **kwargs)


class GameDatabasePrefsWindow(BasePrefsWindow):
    def __init__(self, parent=None):
        super().__init__(parent, title=gettext("Game database preferences"))
        self.panel = GameDatabaseSettingsPage(self)
        self.layout.add(self.panel, fill=True, expand=True)
