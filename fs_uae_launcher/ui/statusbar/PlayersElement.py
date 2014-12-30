from fsui import Image
from ...Config import Config
from ...I18N import gettext
from .StatusElement import StatusElement


class PlayersElement(StatusElement):

    def __init__(self, parent):
        StatusElement.__init__(self, parent)
        self.icon = Image("fs_uae_launcher:res/16/user.png")
        self.text = gettext("N/A")
        self.active = False

        self.players = ""

        Config.add_listener(self)
        self.on_config("players", Config.get("players"))

    def on_destroy(self):
        Config.remove_listener(self)

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
