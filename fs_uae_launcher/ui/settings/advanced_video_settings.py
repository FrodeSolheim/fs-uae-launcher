import fsui as fsui
from fs_uae_launcher.I18N import gettext
from fs_uae_launcher.ui.settings.settings_page import SettingsPage


class AdvancedVideoSettingsPage(SettingsPage):
    def __init__(self, parent):
        super().__init__(parent)
        icon = fsui.Icon("video-settings", "pkg:fs_uae_workspace")
        gettext("Advanced Video Settings")
        title = gettext("Advanced Video")
        subtitle = ""
        self.add_header(icon, title, subtitle)

        self.add_option("video_format")

        self.add_section(gettext("OpenGL Settings"))
        self.add_option("fsaa")
        self.add_option("texture_filter")
        self.add_option("texture_format")
