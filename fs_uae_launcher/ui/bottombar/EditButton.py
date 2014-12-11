from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from fsgs.ogd.client import OGDClient
from fsui import ImageButton, Image, Panel
from ...Config import Config
from ...I18N import _, ngettext
from .WebButton import WebButton


class EditButton(WebButton):

    def __init__(self, parent):
        icon = Image("fs_uae_launcher:res/16/pencil.png")
        WebButton.__init__(self, parent, icon)

    def get_url(self):
        variant_uuid = Config.get("variant_uuid", "")
        if not variant_uuid:
            return
        return "http://{0}/game/{1}/edit#{1}".format(
            OGDClient.get_server(), variant_uuid)
