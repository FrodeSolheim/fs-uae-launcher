from fsbc import settings
from fsgs.option import Option
from launcher.i18n import gettext
from launcher.launcher_config import LauncherConfig
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
        if settings.get(Option.PLATFORMS_FEATURE):
            platform_id = LauncherConfig.get(Option.PLATFORM)
        else:
            platform_id = None
        LauncherConfig.load_default_config(platform=platform_id)
        # Settings.set("config_changed", "1")
        LauncherSettings.set("parent_uuid", "")
