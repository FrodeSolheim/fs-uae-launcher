import fsui
from launcher.ui.settings.settings_page import SettingsPage
from ...i18n import gettext


class GameDatabaseSettingsPage(SettingsPage):
    def __init__(self, parent):
        super().__init__(parent)
        icon = fsui.Icon("database-settings", "pkg:workspace")
        gettext("Game Database Settings")
        title = gettext("Game Database")
        subtitle = ""
        self.add_header(icon, title, subtitle)

        self.add_option("database_show_games")
        self.add_option("database_show_adult")
