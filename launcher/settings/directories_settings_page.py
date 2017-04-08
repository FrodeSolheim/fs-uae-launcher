import fsui
from launcher.res import gettext
from launcher.settings.settings_page import SettingsPage


class DirectoriesSettingsPage(SettingsPage):
    def __init__(self, parent):
        super().__init__(parent)
        icon = fsui.Icon("settings", "pkg:workspace")
        self.add_header(icon, gettext("Directories"))
