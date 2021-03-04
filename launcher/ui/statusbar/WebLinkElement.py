from fsbc.desktop import open_url_in_browser
from fsui import HorizontalLayout, Image, Menu
from launcher.context import get_config
from launcher.i18n import gettext
from launcher.launcher_config import LauncherConfig
from launcher.ui.statusbar.StatusElement import StatusElement

url_descriptions = [
    ("database_url", "Game Database Entry"),
    ("homepage_url", "Game Home Page"),
    ("longplay_url", "Longplay Video"),
    ("hol_url", "Hall of Light Entry"),
    ("lemon_url", "LemonAmiga Entry"),
    ("wikipedia_url", "Wikipedia Entry"),
    ("mobygames_url", "MobyGames Entry"),
    ("amigamemo_url", "AmigaMemo Entry"),
    ("thelegacy_url", "TheLegacy Entry"),
    ("whdload_url", "WHDLoad Slave Info"),
]

url_keys = set([x[0] for x in url_descriptions])


class WebLinkElement(StatusElement):
    def __init__(self, parent):
        StatusElement.__init__(self, parent)
        # self.set_min_width(140)
        self.layout = HorizontalLayout()
        self.icon = Image("launcher:/data/16x16/world_link.png")
        self.right_icon = Image("launcher:/data/16x16/drop_down_arrow.png")
        self.right_icon_disabled = Image(
            "launcher:/data/16x16/drop_down_arrow_disabled.png"
        )
        # self.inactive_icon = self.active_icon.grey_scale()

        self.text = gettext("Web Links")

        config = get_config(self)
        config.add_listener(self)
        self.on_config("protection", config.get("protection"))

        self.have = set()
        for key in url_keys:
            self.on_config(key, config.get(key))

    def on_left_down(self):
        config = get_config(self)
        if len(self.have) == 0:
            return
        menu = Menu()
        for key, description in url_descriptions:
            value = config.get(key, "")
            if value:
                menu.add_item(description, create_open_url_function(value))
        self.popup_menu(menu)

    def on_destroy(self):
        config = get_config(self)
        config.remove_listener(self)
        super().on_destroy()

    def on_config(self, key, value):
        if key in url_keys:
            if value:
                self.have.add(key)
            elif key in self.have:
                self.have.remove(key)
            old_active = self.active
            self.active = len(self.have) > 0
            if old_active != self.active:
                self.refresh()


def create_open_url_function(value):
    def open_url():
        open_url_in_browser(value)

    return open_url
