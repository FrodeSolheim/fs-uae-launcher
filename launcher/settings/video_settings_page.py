import fsui
from fsgamesys.options.option import Option
from launcher.i18n import gettext
from launcher.settings.settings_page import SettingsPage
from system.prefs.components.notworking import PrefsNotWorkingWarningPanel


class VideoSettingsPage(SettingsPage):
    def __init__(self, parent):
        super().__init__(parent)
        # icon = fsui.Icon("video-settings", "pkg:workspace")
        # gettext("Video Settings")
        # title = gettext("Video")
        # subtitle = ""
        # self.add_header(icon, title, subtitle)
        PrefsNotWorkingWarningPanel(parent=self)
        self.layout.add_spacer(20)

        self.add_option("fullscreen", margin_top=0)
        self.add_option("monitor")

        self.add_section(gettext("Scaling & Filters"))
        self.add_option("zoom")
        self.add_option("keep_aspect")

        # self.add_section(gettext("Filters"))
        self.add_option("scanlines")
        self.add_option("rtg_scanlines")

        self.add_section(gettext("Video Synchronization"))
        # FIXME: Move 640 to constants
        label = fsui.MultiLineLabel(
            self,
            gettext(
                "Enabling the following option will synchronize the emulation "
                "to the display when the emulation refresh rate matches the "
                "screen refresh rate."
            ),
            640,
        )
        self.layout.add(label, fill=True, margin_top=0)
        self.video_sync_group = self.add_option("video_sync")

        self.add_section(gettext("Advanced"))
        self.add_option(Option.FULLSCREEN_MODE)
        self.add_option(Option.VIDEO_FORMAT)
        self.low_latency_group = self.add_option(
            Option.LOW_LATENCY_VSYNC, margin_bottom=0
        )
