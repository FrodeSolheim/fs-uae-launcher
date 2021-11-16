import fsui
from fsbc import settings
from fsgamesys import openretro
from fsgamesys.platforms.platform import Platform
from fswidgets.widget import Widget
from launcher.i18n import gettext
from launcher.option import Option
from launcher.settings.option_ui import OptionUI
from launcher.settings.platformsettingsdialog import PlatformSettingsDialog
from launcher.settings.settings_page import SettingsPage
from launcher.ui.IconButton import IconButton


class GamePlatformsSettingsPage(SettingsPage):
    def __init__(self, parent: Widget) -> None:
        super().__init__(parent)
        icon = fsui.Icon("database-settings", "pkg:workspace")
        title = gettext("Game Platforms")
        subtitle = ""
        self.add_header(icon, title, subtitle)

        self.hori_layout = None
        self.hori_counter = 0

        if openretro or settings.get(Option.PLATFORMS_FEATURE) == "1":
            # self.add_section(gettext("Game Databases"))

            label = fsui.MultiLineLabel(
                self,
                gettext(
                    "Note: This is an experimental feature. "
                    "Additional plugins are needed."
                ),
                640,
            )
            self.layout.add(label, margin_top=20, margin_bottom=20)

            self.add_database_option(
                Platform.CPC, Option.CPC_DATABASE, "Amstrad CPC"
            )
            self.add_database_option(
                Platform.ARCADE, Option.ARCADE_DATABASE, "Arcade"
            )
            self.add_database_option(
                Platform.A7800, Option.A7800_DATABASE, "Atari 7800"
            )
            self.add_database_option(
                Platform.C64, Option.C64_DATABASE, "Commodore 64"
            )
            self.add_database_option(Platform.DOS, Option.DOS_DATABASE, "DOS")
            self.add_database_option(
                Platform.GB, Option.GB_DATABASE, "Game Boy"
            )
            self.add_database_option(
                Platform.GBA, Option.GBA_DATABASE, "Game Boy Advance"
            )
            self.add_database_option(
                Platform.GBC, Option.GBC_DATABASE, "Game Boy Color"
            )
            self.add_database_option(
                Platform.SMS, Option.SMS_DATABASE, "Master System"
            )
            self.add_database_option(
                Platform.SMD, Option.SMD_DATABASE, "Mega Drive"
            )
            self.add_database_option(
                Platform.NEOGEO, Option.NEOGEO_DATABASE, "Neo-Geo"
            )
            self.add_database_option(
                Platform.NES, Option.NES_DATABASE, "Nintendo"
            )
            self.add_database_option(
                Platform.PSX, Option.PSX_DATABASE, "PlayStation"
            )
            self.add_database_option(
                Platform.SNES, Option.SNES_DATABASE, "Super Nintendo"
            )
            self.add_database_option(
                Platform.ST, Option.ST_DATABASE, "Atari ST"
            )
            self.add_database_option(
                Platform.TG16, Option.TG16_DATABASE, "TurboGrafx-16"
            )
            self.add_database_option(
                Platform.TGCD, Option.TGCD_DATABASE, "TurboGrafx-CD"
            )
            self.add_database_option(
                Platform.ZXS, Option.ZXS_DATABASE, "ZX Spectrum"
            )

            # label = fsui.MultiLineLabel(
            #     self, gettext(
            #         "Note: Support for additional game databases is an "
            #         "experimental feature and does not provide the "
            #         "same level of maturity as Amiga/CDTV/CD32. "
            #         "Also, additional plugins are needed to play the "
            #         "games."), 640)
            # self.layout.add(label, margin_top=20)

    def add_database_option(self, platform, name, description=""):
        self.options_on_page.add(name)
        group = OptionUI.create_group(
            self, name, description=description, help_button=False
        )

        if self.hori_counter % 2 == 0:
            self.hori_layout = fsui.HorizontalLayout()
            self.layout.add(
                self.hori_layout,
                fill=True,
                margin_top=10,
                margin_bottom=10,
                margin_left=-10,
                margin_right=-10,
            )

        self.hori_layout.add(
            group,
            fill=True,
            expand=-1,
            margin=10,
            margin_top=0,
            margin_bottom=0,
        )
        self.hori_layout.add(
            PlatformSettingsButton(self, platform), margin_right=10
        )

        if self.hori_counter % 2 == 0:
            self.hori_layout.add_spacer(0)
        self.hori_counter += 1


class PlatformSettingsButton(IconButton):
    def __init__(self, parent, platform):
        super().__init__(parent, "16x16/settings.png")
        self.platform = platform
        self.set_enabled(
            len(PlatformSettingsDialog.option_list_for_platform(platform)) > 0
        )

    def on_activate(self):
        PlatformSettingsDialog.open(self.window, self.platform)
