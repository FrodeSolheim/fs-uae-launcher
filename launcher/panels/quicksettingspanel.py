import fsui
from fsgs.option import Option
from fsgs.platform import Platform
from launcher.i18n import gettext
from launcher.settings.fullscreenmodebutton import FullscreenModeButton
from launcher.settings.monitorbutton import MonitorButton
from launcher.settings.option_ui import OptionUI
from launcher.settings.settings_dialog import SettingsDialog
from launcher.settings.videosynccheckbox import VideoSyncCheckBox
from launcher.ui.IconButton import IconButton
from launcher.ui.behaviors.configbehavior import ConfigBehavior
from launcher.ui.behaviors.platformbehavior import PlatformShowBehavior, \
    AMIGA_PLATFORMS

MEDNAFEN = [Platform.SNES, Platform.GB, Platform.GBA, Platform.GBC,
           Platform.SMD, Platform.SMS, Platform.TG16]
SCALING = [Platform.C64] + MEDNAFEN
STRETCHING = [Platform.C64, Platform.DOS, Platform.ZXS] + MEDNAFEN
EFFECTS = [Platform.C64, Platform.DOS, Platform.ZXS] + MEDNAFEN
BORDER = [Platform.C64, Platform.ZXS] + MEDNAFEN
SMOOTHING = [] + MEDNAFEN
CROPPING = [Platform.ZXS]


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

        self.add_option(Option.KEEP_ASPECT, text=gettext("Keep Aspect"),
                        platforms=AMIGA_PLATFORMS)
        self.add_option(Option.SCALE, text=None, platforms=SCALING)
        self.add_option(Option.STRETCH, text=None, platforms=STRETCHING)
        self.add_option(Option.BORDER, text=None, platforms=BORDER)

        self.add_option(Option.SMOOTHING, text=None, platforms=SMOOTHING)
        self.add_option(Option.EFFECT, text=None, platforms=EFFECTS)

        # self.add_option(Option.CROP, text=None, platforms=CROPPING)

        # self.add_option(Option.ZXS_DRIVER, [Platform.ZXS])
        self.add_option(Option.DOS_EMULATOR, [Platform.DOS])
        self.add_option(Option.AUTO_LOAD, [Platform.DOS, Platform.ZXS])
        self.add_option(Option.AUTO_QUIT, [Platform.DOS])
        self.add_option(Option.TURBO_LOAD, [Platform.ZXS])
        self.add_option(Option.C64_PALETTE, [Platform.C64])

        self.layout.add_spacer(expand=True)

        hori_layout = fsui.HorizontalLayout()
        hori_layout.add_spacer(expand=True)
        self.video_sync_checkbox = VideoSyncCheckBox(self)
        hori_layout.add(self.video_sync_checkbox, margin_right=10)
        self.layout.add(hori_layout, fill=True)
        self.monitor_button = MonitorButton(self)
        hori_layout.add(self.monitor_button, fill=True, margin_right=10)
        self.fullscreen_mode_button = FullscreenModeButton(self)
        hori_layout.add(self.fullscreen_mode_button, fill=True, margin_right=10)
        self.layout.add_spacer(10)

        ConfigBehavior(self, [Option.PLATFORM])

    def add_option(self, option, platforms=None, text=""):
        panel = fsui.Panel(self)
        panel.layout = fsui.VerticalLayout()
        panel.layout.add(
            OptionUI.create_group(
                panel, option, text, thin=True, help_button=False),
            fill=True)
        self.layout.add(panel, fill=True, margin=10)
        if platforms:
            PlatformShowBehavior(panel, platforms)

    def on_platform_config(self, _):
        self.layout.update()

    def on_settings_button(self):
        SettingsDialog.open(self.window)

    def get_min_height(self):
        # Because we add a lot of controls, force min size to 0 to avoid
        # this control reporting too large min height at startup.
        return 0
