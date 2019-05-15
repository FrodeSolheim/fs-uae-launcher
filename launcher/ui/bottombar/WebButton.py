from fsbc.desktop import open_url_in_browser
from fsgs.network import openretro_url_prefix
from fsui import Image, Panel
from ...launcher_config import LauncherConfig
from ..skin import Skin


class WebButton(Panel):

    def __init__(self, parent, icon=None):
        if icon is not None:
            self.icon = icon
        else:
            self.icon = Image("launcher:res/16/world.png")
        Panel.__init__(self, parent, paintable=True)
        # self.set_tooltip(tooltip)
        LauncherConfig.add_listener(self)
        self.on_config("variant_uuid", "")

    def on_destroy(self):
        LauncherConfig.remove_listener(self)
        pass

    def get_min_width(self):
        return 32

    def get_min_height(self):
        return 24

    def get_url(self):
        variant_uuid = LauncherConfig.get("variant_uuid", "")
        if not variant_uuid:
            return
        return "{0}/game/{1}".format(
            openretro_url_prefix(), variant_uuid)

    def on_left_down(self):
        url = self.get_url()
        if url:
            open_url_in_browser(url)

    def on_config(self, key, value):
        if key == "variant_uuid":
            if value:
                if not self.is_enabled():
                    self.enable()
                    # self.refresh()
                    self.show()
                    self.set_hand_cursor()
            else:
                if self.is_enabled():
                    self.disable()
                    self.hide()
                    # self.refresh()
                    # self.set_default_cursor()

    def on_paint(self):
        dc = self.create_dc()
        dc.clear(Skin.get_background_color())
        if self.is_enabled():
            dc.draw_image(self.icon, 8, 4)
        else:
            pass
