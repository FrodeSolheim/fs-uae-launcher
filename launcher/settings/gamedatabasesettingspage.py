from launcher.settings.option_ui import OptionUI

import fsui
from fsbc import settings
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

        if settings.get(Option.PLATFORMS_FEATURE) == "1":
            self.add_section(gettext("Additional Databases"))

            label = fsui.MultiLineLabel(
                self, gettext(
                    "Note: This is an experimental feature. "
                    "Additional plugins are needed."), 640)
            self.layout.add(label, margin_top=20, margin_bottom=20)

            self.add_database_option(Option.CPC_DATABASE, "Amstrad CPC")
            self.add_database_option(Option.ARCADE_DATABASE, "Arcade")
            self.add_database_option(Option.ATARI_DATABASE, "Atari ST")
            self.add_database_option(Option.C64_DATABASE, "Commodore 64")
            self.add_database_option(Option.DOS_DATABASE, "DOS")
            self.add_database_option(Option.GB_DATABASE, "Game Boy")
            self.add_database_option(Option.GBA_DATABASE, "Game Boy Advance")
            self.add_database_option(Option.GBC_DATABASE, "Game Boy Color")
            self.add_database_option(Option.NES_DATABASE, "Nintendo")
            self.add_database_option(Option.PSX_DATABASE, "PlayStation")
            self.add_database_option(Option.SNES_DATABASE, "Super Nintendo")
            self.add_database_option(Option.ZXS_DATABASE, "ZX Spectrum")

            # label = fsui.MultiLineLabel(
            #     self, gettext(
            #         "Note: Support for additional game databases is an "
            #         "experimental feature and does not provide the "
            #         "same level of maturity as Amiga/CDTV/CD32. "
            #         "Also, additional plugins are needed to play the "
            #         "games."), 640)
            # self.layout.add(label, margin_top=20)

    def add_database_option(self, name, description=""):
        self.options_on_page.add(name)
        group = OptionUI.create_group(
            self, name, description=description, help_button=False)

        if self.hori_counter % 2 == 0:
            self.hori_layout = fsui.HorizontalLayout()
            self.layout.add(
                self.hori_layout, fill=True, margin_top=10, margin_bottom=10,
                margin_left=-10, margin_right=-10)
        self.hori_layout.add(group, fill=True, expand=-1, margin=10,
                             margin_top=0, margin_bottom=0)
        if self.hori_counter % 2 == 0:
            self.hori_layout.add_spacer(10)
        self.hori_counter += 1
