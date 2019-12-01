import fsui
from launcher.i18n import gettext
from launcher.option import Option
from launcher.settings.settings_page import SettingsPage


class GameDatabaseSettingsPage(SettingsPage):
    def __init__(self, parent):
        super().__init__(parent)
        icon = fsui.Icon("database-settings", "pkg:workspace")
        gettext("Game Database Settings")
        title = gettext("Game Database")
        subtitle = ""
        self.add_header(icon, title, subtitle)

        self.hori_layout = None
        self.hori_counter = 0

        self.add_option(Option.DATABASE_SHOW_GAMES)
        self.add_option(Option.DATABASE_SHOW_ADULT)
        self.add_option(Option.DATABASE_SHOW_UNPUBLISHED)
