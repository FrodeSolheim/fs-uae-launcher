import fsui
from fswidgets.widget import Widget
from launcher.res import gettext
from launcher.settings.settings_page import SettingsPage


class DirectoriesSettingsPage(SettingsPage):
    def __init__(self, parent: Widget) -> None:
        super().__init__(parent)
        icon = fsui.Icon("settings", "pkg:workspace")
        self.add_header(icon, gettext("Directories"))
