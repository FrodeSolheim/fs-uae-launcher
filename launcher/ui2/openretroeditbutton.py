from fsgamesys.options.constants2 import VARIANT_UUID__
from fstd.desktop import open_url_in_browser
from fswidgets.widget import Widget
from launcher.context import get_config
from launcher.ui.IconButton import IconButton


class OpenRetroEditButton(IconButton):
    def __init__(self, parent: Widget) -> None:
        super().__init__(parent, "16x16/world_link.png")
        self.activated.connect(self.__activated)

    def __activated(self) -> None:
        config = get_config(self)
        variant_uuid = config.get(VARIANT_UUID__)
        if variant_uuid:
            url = f"https://openretro.org/game/{variant_uuid}/edit"
            open_url_in_browser(url)
