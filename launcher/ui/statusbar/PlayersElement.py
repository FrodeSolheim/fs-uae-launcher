from fsui import Image

from ...i18n import gettext
from ...launcher_config import LauncherConfig
from .StatusElement import StatusElement


class PlayersElement(StatusElement):
    def __init__(self, parent):
        StatusElement.__init__(self, parent)
        self.icon = Image("launcher:res/16x16/user.png")
        self.text = gettext("N/A")
        self.active = False

        self.players = ""

        LauncherConfig.add_listener(self)
        self.on_config("players", LauncherConfig.get("players"))

    def on_destroy(self):
        LauncherConfig.remove_listener(self)

    def on_config(self, key, value):
        if key == "players":
            if value != self.players:
                self.players = value
                if value:
                    self.text = value
                else:
                    self.text = gettext("N/A")
                self.active = bool(value)
                self.refresh()

    def get_min_width(self):
        return 96
