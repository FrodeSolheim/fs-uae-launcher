from fsbc.settings import Settings
from fsgs import openretro
from fsgs.options.option import Option
from launcher.i18n import gettext
from launcher.launcher_config import LauncherConfig
from launcher.ui.IconButton import IconButton
from fsgs.options.constants2 import PARENT_UUID
from launcher.context import get_config


class NewConfigButton(IconButton):
    def __init__(self, parent):
        super().__init__(parent, "new_button.png")
        self.set_tooltip(gettext("New config"))

    def on_activate(self):
        self.new_config(get_config(self))

    @staticmethod
    def new_config(config):
        settings = Settings().instance()
        if openretro or settings.get(Option.PLATFORMS_FEATURE):
            platform_id = config.get(Option.PLATFORM)
        else:
            platform_id = None

        LauncherConfig.load_default_config(platform=platform_id)

        # Settings.set("config_changed", "1")
        settings.set(PARENT_UUID, "")
