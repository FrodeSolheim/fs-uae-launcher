import traceback

import fsui
from fsgamesys.options.option import Option
from fsgamesys.platforms.platform import Platform
from launcher.context import get_config
from launcher.i18n import gettext
from launcher.option import options
from launcher.settings.fullscreenmodebutton import FullscreenModeButton
from launcher.settings.monitorbutton import MonitorButton
from launcher.settings.option_ui import OptionUI
from launcher.settings.platformsettingsdialog import PlatformSettingsDialog
from launcher.settings.settings_dialog import SettingsDialog
from launcher.settings.videosynccheckbox import VideoSyncCheckBox
from launcher.ui.IconButton import IconButton
from launcher.ui.behaviors.configbehavior import ConfigBehavior
from launcher.ui.behaviors.platformbehavior import (
    PlatformShowBehavior,
    AMIGA_PLATFORMS,
    PlatformEnableBehavior,
)
from launcher.ui.behaviors.settingsbehavior import SettingsBehavior

MEDNAFEN = [
    Platform.SNES,
    Platform.NES,
    Platform.GB,
    Platform.GBA,
    Platform.GBC,
    Platform.PSX,
    Platform.SMD,
    Platform.SMS,
    Platform.TG16,
    Platform.TGCD,
]
SCALING = [Platform.C64] + MEDNAFEN
STRETCHING = [Platform.C64, Platform.DOS, Platform.ZXS] + MEDNAFEN
EFFECTS = [Platform.C64, Platform.DOS, Platform.ZXS] + MEDNAFEN
BORDER = [Platform.C64, Platform.ZXS]
# BORDER += MEDNAFEN
SMOOTHING = [] + MEDNAFEN
CROPPING = [Platform.ZXS]

SCALING += AMIGA_PLATFORMS
STRETCHING += AMIGA_PLATFORMS
STRETCHING += [Platform.ARCADE, Platform.NEOGEO]

BEZEL = (
    AMIGA_PLATFORMS
    + MEDNAFEN
    + [
        Platform.ARCADE,
        Platform.NEOGEO,
        Platform.ZXS,
        Platform.DOS,
        Platform.C64,
    ]
)
CHEATS = MEDNAFEN + [Platform.ARCADE, Platform.NEOGEO]


class QuickSettingsPanel(fsui.Panel):
    def __init__(self, parent, fsgc):
        self.fsgc = fsgc
        super().__init__(parent)
        self.layout = fsui.VerticalLayout()

        hori_layout = fsui.HorizontalLayout()
        self.layout.add(hori_layout, fill=True)
        heading_label = fsui.HeadingLabel(self, gettext("Settings"))
        hori_layout.add(heading_label, margin=10)
        hori_layout.add_spacer(0, expand=True)
        settings_button = IconButton(self, "16x16/more.png")
        settings_button.activated.connect(self.on_settings_button)
        hori_layout.add(settings_button, margin_right=10)
        self.layout.add_spacer(0)

        # button = fsui.Button(self, "Platform Settings")
        # button.activated.connect(self.on_platform_settings_button)
        # self.layout.add(button, margin=10, fill=True)

        # self.add_option(Option.KEEP_ASPECT, text=gettext("Keep Aspect"),
        #                 platforms=AMIGA_PLATFORMS)
        self.add_option(Option.SCALE, text=None, enable=SCALING)
        self.add_option(Option.STRETCH, text=None, enable=STRETCHING)
        self.add_option(Option.BEZEL, text=None, enable=BEZEL)

        self.add_option(Option.EFFECT, text=None, enable=EFFECTS)

        self.add_option(Option.ZOOM, text=None, platforms=AMIGA_PLATFORMS)
        self.add_option(Option.BORDER, text=None, platforms=BORDER)

        # self.add_option(Option.SMOOTHING, text=None, platforms=SMOOTHING)

        # self.add_option(Option.CROP, text=None, platforms=CROPPING)

        # if fsgc.settings[Option.DEVELOPER_MODE] == "1":
        #     pass
        #     # self.add_option(Option.ZXS_DRIVER, [Platform.ZXS])
        #     # self.add_option(Option.DOS_EMULATOR, [Platform.DOS])
        # self.add_option(Option.NES_EMULATOR, [Platform.NES])

        self.add_option(
            Option.AUTO_LOAD, [Platform.CPC, Platform.DOS, Platform.ZXS]
        )
        self.add_option(Option.AUTO_QUIT, [Platform.DOS])
        self.add_option(Option.TURBO_LOAD, [Platform.ZXS])

        # self.add_option(Option.FRAME, text=None, platforms=BEZEL)
        # self.add_option(Option.BEZEL, text=None, platforms=BEZEL)

        # self.add_option(Option.CHEATS, platforms=CHEATS)

        quick_settings = fsgc.settings[Option.QUICK_SETTINGS_OPTIONS]
        for option in quick_settings.split(","):
            option = option.strip().lower()
            if "[" in option:
                # For future use of e.g.:
                # option1[platform1,platform2],option2[platform,...]
                option, platforms = option.split("[", 1)
            else:
                platforms = []
            if option in options:
                try:
                    self.add_option(option)
                except Exception:
                    print("Error adding quick setting")
                    traceback.print_exc()

        self.layout.add_spacer(expand=True)

        self.add_option(
            Option.AMIGA_EMULATOR,
            [Platform.AMIGA, Platform.CD32, Platform.CDTV],
        )
        self.add_option(Option.ARCADE_EMULATOR, [Platform.ARCADE])
        self.add_option(Option.CPC_EMULATOR, [Platform.CPC])
        self.add_option(Option.NES_EMULATOR, [Platform.NES])
        self.add_option(Option.SNES_EMULATOR, [Platform.SNES])
        self.add_option(Option.ST_EMULATOR, [Platform.ST])
        self.add_option(Option.ZXS_EMULATOR, [Platform.ZXS])

        hori_layout = fsui.HorizontalLayout()
        # hori_layout.add_spacer(expand=True)
        self.platform_settings_button = fsui.Button(self, "Platform Settings")
        self.platform_settings_button.activated.connect(
            self.on_platform_settings_button
        )
        hori_layout.add(self.platform_settings_button, expand=True, margin=10)
        self.layout.add(hori_layout, fill=True)

        hori_layout = fsui.HorizontalLayout()
        hori_layout.add_spacer(expand=True)
        self.video_sync_checkbox = VideoSyncCheckBox(self)
        hori_layout.add(self.video_sync_checkbox, margin_right=10)
        self.layout.add(hori_layout, fill=True)
        self.monitor_button = MonitorButton(self)
        hori_layout.add(self.monitor_button, fill=True, margin_right=10)
        if False:
            self.fullscreen_mode_button = FullscreenModeButton(self)
            hori_layout.add(
                self.fullscreen_mode_button, fill=True, margin_right=10
            )
        self.layout.add_spacer(10)

        ConfigBehavior(self, [Option.PLATFORM])
        SettingsBehavior(self, [Option.G_SYNC])

    def add_option(self, option, platforms=None, enable=None, text=""):
        panel = fsui.Panel(self)
        panel.layout = fsui.VerticalLayout()
        panel.layout.add(
            OptionUI.create_group(
                panel, option, text, thin=True, help_button=False
            ),
            fill=True,
        )
        self.layout.add(panel, fill=True, margin=10)
        if platforms:
            PlatformShowBehavior(panel, platforms)
        elif enable:
            PlatformEnableBehavior(panel, enable)

    def on_platform_config(self, value):
        self.layout.update()
        self.platform_settings_button.set_enabled(
            len(PlatformSettingsDialog.option_list_for_platform(value)) > 0
        )

    def on_g_sync_setting(self, value):
        self.video_sync_checkbox.set_enabled(value != "1")

    def on_settings_button(self):
        SettingsDialog.open(self.window)

    def on_platform_settings_button(self):
        platform = get_config(self).get("platform")
        if platform:
            PlatformSettingsDialog.open(self.window, platform)

    def get_min_height(self):
        # Because we add a lot of controls, force min size to 0 to avoid
        # this control reporting too large min height at startup.
        return 0
