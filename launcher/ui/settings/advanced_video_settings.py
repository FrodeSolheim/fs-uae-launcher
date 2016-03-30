import fsui as fsui
from launcher.i18n import gettext
from launcher.ui.settings.settings_page import SettingsPage


class AdvancedVideoSettingsPage(SettingsPage):
    def __init__(self, parent):
        super().__init__(parent)
        icon = fsui.Icon("video-settings", "pkg:workspace")
        gettext("Advanced Video Settings")
        title = gettext("Advanced Video")
        subtitle = ""
        self.add_header(icon, title, subtitle)

        self.add_option("video_format")

        self.add_section(gettext("OpenGL Settings"))
        self.add_option("fsaa")
        self.add_option("texture_filter")
        self.add_option("texture_format")

        self.add_section(gettext("Video Synchronization"))
        self.low_latency_group = self.add_option("low_latency_vsync")
        self.sync_method_label = fsui.MultiLineLabel(self, gettext(
            "Depending on your OS and OpenGL drivers, video synchronization "
            "can use needlessly much CPU (esp. applies to "
            "Linux). You can experiment with different sync methods "
            "to improve performance."), 640)
        self.layout.add(self.sync_method_label, fill=True, margin_top=20)
        self.sync_method_group = self.add_option("video_sync_method")
