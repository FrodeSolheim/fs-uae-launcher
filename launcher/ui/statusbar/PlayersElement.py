from fsui import Image
from launcher.ui.statusbar.StatusElement import StatusElement
from launcher.i18n import gettext
from launcher.context import get_config


class PlayersElement(StatusElement):
    def __init__(self, parent):
        StatusElement.__init__(self, parent)
        self.icon = Image("launcher:res/16x16/user.png")
        self.text = gettext("N/A")
        self.active = False

        self.players = ""

        config = get_config(self)
        config.add_listener(self)
        self.on_config("players", config.get("players"))

    def on_destroy(self):
        config = get_config(self)
        config.remove_listener(self)
        super().on_destroy()

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
