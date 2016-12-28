import fsui
from launcher.i18n import gettext
from launcher.option import Option
from launcher.ui.settings.settings_page import SettingsPage


class GameDatabaseSettingsPage(SettingsPage):
    def __init__(self, parent):
        super().__init__(parent)
        icon = fsui.Icon("database-settings", "pkg:workspace")
        gettext("Game Database Settings")
        title = gettext("Game Database")
        subtitle = ""
        self.add_header(icon, title, subtitle)

        self.add_option(Option.DATABASE_SHOW_GAMES)
        self.add_option(Option.DATABASE_SHOW_ADULT)
        self.add_option(Option.DATABASE_SHOW_UNPUBLISHED)

        self.add_section(gettext("Additional Databases"))
        self.add_option(Option.DATABASE_GB, "Game Boy")
        self.add_option(Option.DATABASE_GBC, "Game Boy Color")
        self.add_option(Option.DATABASE_GBA, "Game Boy Advance")
        self.add_option(Option.DATABASE_NES, "Nintendo")
        self.add_option(Option.DATABASE_SNES, "Super Nintendo")
        label = fsui.MultiLineLabel(
            self, gettext("Note: Support for additional game databases is an "
                          "experimental feature and does not provide the "
                          "same level of maturity as Amiga/CDTV/CD32. "
                          "Also, additional plugins are needed to play the "
                          "games."), 640)
        self.layout.add(label, margin_top=20)
