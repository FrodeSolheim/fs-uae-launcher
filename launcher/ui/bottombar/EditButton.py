from fsgs.ogd.client import OGDClient
from fsui import Image
from ...launcher_config import LauncherConfig
from .WebButton import WebButton


class EditButton(WebButton):

    def __init__(self, parent):
        icon = Image("launcher:res/16/pencil.png")
        WebButton.__init__(self, parent, icon)

    def get_url(self):
        variant_uuid = LauncherConfig.get("variant_uuid", "")
        if not variant_uuid:
            return
        return "http://{0}/game/{1}/edit#{1}".format(
            OGDClient.get_server(), variant_uuid)
