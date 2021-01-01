from fsbc.desktop import open_url_in_browser
from fsgs.options.constants2 import VARIANT_UUID__
from launcher.ui.IconButton import IconButton
from launcher.context import get_config


class OpenRetroEditButton(IconButton):
    def __init__(self, parent):
        super().__init__(parent, "16x16/world_link.png")
        self.activated.connect(self.__activated)

    def __activated(self):
        config = get_config(self)
        variant_uuid = config.get(VARIANT_UUID__)
        if variant_uuid:
            url = f"https://openretro.org/game/{variant_uuid}/edit"
            open_url_in_browser(url)
