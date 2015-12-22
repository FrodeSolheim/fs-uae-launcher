import fsui as fsui
from fs_uae_launcher.ui.settings.settings_page import SettingsPage
from ...I18N import gettext


class GameDatabaseSettingsPage(SettingsPage):
    def __init__(self, parent):
        super().__init__(parent)
        icon = fsui.Icon("database-settings", "pkg:fs_uae_workspace")
        gettext("Game Database Settings")
        title = gettext("Game Database")
        subtitle = ""
        self.add_header(icon, title, subtitle)

        self.add_option("database_show_games")
        self.add_option("database_show_adult")
