import fsui
from fswidgets.widget import Widget
from launcher.i18n import gettext
from launcher.option import Option
from launcher.settings.settings_page import SettingsPage


class ExperimentalFeaturesPage(SettingsPage):
    def __init__(self, parent: Widget) -> None:
        super().__init__(parent)
        icon = fsui.Icon("settings", "pkg:workspace")
        title = gettext("Experimental Features")
        subtitle = ""
        self.add_header(icon, title, subtitle)

        self.add_option(Option.NETPLAY_FEATURE)
        self.add_option(Option.LAUNCHER_CONFIG_FEATURE)
