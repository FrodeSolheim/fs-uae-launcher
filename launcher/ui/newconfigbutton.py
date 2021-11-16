from typing import Optional

from fsbc.settings import Settings
from fsgamesys import openretro
from fsgamesys.options.constants2 import PARENT_UUID
from fsgamesys.options.option import Option
from fsgamesys.product import Product
from fswidgets.widget import Widget
from launcher.context import get_config
from launcher.i18n import gettext
from launcher.launcher_config import LauncherConfig
from launcher.ui.IconButton import IconButton


class NewConfigButton(IconButton):
    def __init__(self, parent: Widget) -> None:
        super().__init__(parent, "new_button.png")
        self.set_tooltip(gettext("New config"))

    def on_activate(self) -> None:
        self.new_config(get_config(self))

    @staticmethod
    def new_config(config) -> None:
        settings = Settings().instance()
        platform_id: Optional[str]
        if Product.default_platform_id:
            platform_id = Product.default_platform_id
        elif openretro or settings.get(Option.PLATFORMS_FEATURE):
            platform_id = config.get(Option.PLATFORM)
        else:
            platform_id = None

        LauncherConfig.load_default_config(platform=platform_id)

        # Settings.set("config_changed", "1")
        settings.set(PARENT_UUID, "")
