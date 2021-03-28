from launcher.i18n import gettext
from launcher.settings.gamedatabasesettingspage import GameDatabaseSettingsPage
from launcher.system.prefs.components.baseprefswindow import BasePrefsWindow


class GameDatabasePrefsWindow(BasePrefsWindow):
    def __init__(self, parent):
        super().__init__(parent, title=gettext("Game database preferences"))
        self.panel = GameDatabaseSettingsPage(self)
        self.layout.add(self.panel, fill=True, expand=True)
