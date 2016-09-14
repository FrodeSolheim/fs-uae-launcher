import fsui
from launcher.option import Option
from launcher.ui.settings.settings_page import SettingsPage


class ArcadeSettingsPage(SettingsPage):
    def __init__(self, parent):
        super().__init__(parent)
        icon = fsui.Icon("settings", "pkg:workspace")
        self.add_header(icon, "FS-UAE Arcade")
        self.add_option(Option.ARCADE_FULLSCREEN)
