import fsui
from launcher.i18n import gettext
from launcher.option import Option
from launcher.settings.settings_page import SettingsPage
from system.prefs.components.notworking import PrefsNotWorkingWarningPanel


class AdvancedVideoSettingsPage(SettingsPage):
    def __init__(self, parent):
        super().__init__(parent)

        PrefsNotWorkingWarningPanel(parent=self)
        self.layout.add_spacer(20)

        icon = fsui.Icon("video-settings", "pkg:workspace")
        gettext("Advanced Video Settings")
        title = gettext("Advanced Video")
        subtitle = ""
        self.add_header(icon, title, subtitle)

        self.add_option(Option.FULLSCREEN_MODE)
        self.add_option(Option.VIDEO_FORMAT)
        self.low_latency_group = self.add_option(Option.LOW_LATENCY_VSYNC)

        self.add_section(gettext("OpenGL Settings"))
        self.add_option(Option.FSAA)
        self.add_option(Option.TEXTURE_FILTER)
        self.add_option(Option.TEXTURE_FORMAT)

        # self.add_section(gettext("Video Synchronization"))
        self.sync_method_label = fsui.MultiLineLabel(
            self,
            gettext(
                "Depending on your OS and OpenGL drivers, video synchronization "
                "can use needlessly much CPU (esp. applies to "
                "Linux). You can experiment with different sync methods "
                "to improve performance."
            ),
            640,
        )
        self.layout.add(self.sync_method_label, fill=True, margin_top=20)
        self.sync_method_group = self.add_option(Option.VIDEO_SYNC_METHOD)
