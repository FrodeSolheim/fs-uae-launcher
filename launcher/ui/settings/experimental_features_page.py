import fsui as fsui
from launcher.i18n import gettext
from launcher.options import Option
from launcher.ui.settings.settings_page import SettingsPage


class ExperimentalFeaturesPage(SettingsPage):
    def __init__(self, parent):
        super().__init__(parent)
        icon = fsui.Icon("settings", "pkg:workspace")
        title = gettext("Experimental Features")
        subtitle = ""
        self.add_header(icon, title, subtitle)

        # self.add_option(Option.NETPLAY_FATURE)
        self.add_option(Option.CONFIG_FEATURE)
