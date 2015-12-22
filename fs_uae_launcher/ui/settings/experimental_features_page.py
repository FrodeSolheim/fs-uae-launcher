import fsui as fsui
from fs_uae_launcher.I18N import gettext
from fs_uae_launcher.ui.settings.settings_page import SettingsPage


class ExperimentalFeaturesPage(SettingsPage):
    def __init__(self, parent):
        super().__init__(parent)
        icon = fsui.Icon("settings", "pkg:fs_uae_workspace")
        title = gettext("Experimental Features")
        subtitle = ""
        self.add_header(icon, title, subtitle)

        self.add_option("netplay_feature")
        self.add_option("config_feature")
