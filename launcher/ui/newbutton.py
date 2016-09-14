from launcher.launcher_config import LauncherConfig
from launcher.i18n import gettext
from launcher.launcher_settings import LauncherSettings
from launcher.ui.IconButton import IconButton


class NewButton(IconButton):

    def __init__(self, parent):
        super().__init__(parent, "new_button.png")
        self.set_tooltip(gettext("New Config"))

    def on_activate(self):
        self.new_config()

    @staticmethod
    def new_config():
        LauncherConfig.load_default_config()
        # Settings.set("config_changed", "1")
        LauncherSettings.set("parent_uuid", "")
