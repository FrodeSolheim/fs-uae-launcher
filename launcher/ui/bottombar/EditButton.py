from fsgamesys.network import openretro_url_prefix
from fsui import Image
from launcher.context import get_config
from launcher.ui.bottombar.WebButton import WebButton


class EditButton(WebButton):
    def __init__(self, parent):
        icon = Image("launcher:res/16x16/pencil.png")
        WebButton.__init__(self, parent, icon)

    def get_url(self):
        config = get_config(self)
        variant_uuid = config.get("variant_uuid", "")
        if not variant_uuid:
            return
        return "{0}/game/{1}/edit#{1}".format(
            openretro_url_prefix(), variant_uuid
        )
