from fsbc.util import unused
from fsui import Panel, Color, VerticalLayout, HorizontalLayout, Image
from ...launcher_config import LauncherConfig
from ..skin import Skin
from .LanguageElement import LanguageElement
from .PlayersElement import PlayersElement
from .ProtectionElement import ProtectionElement
from .WarningsElement import WarningsElement
from .WebLinkElement import WebLinkElement


class StatusBar(Panel):

    def __init__(self, parent):
        Panel.__init__(self, parent, paintable=True)
        self.set_min_height(29)
        # self.set_background_color(Color(0xd8, 0xd8, 0xd8))
        self.layout = VerticalLayout()
        self.hori_layout = HorizontalLayout()
        if Skin.fws():
            self.top_border_size = 2
        else:
            self.top_border_size = 1
        self.layout.add(self.hori_layout, fill=True, expand=True,
                        margin_top=self.top_border_size)

        element = ProtectionElement(self)
        self.hori_layout.add(element, fill=True)

        element = WarningsElement(self)
        self.hori_layout.add(element, fill=True, expand=True)
        self.hori_layout.add_spacer(16)

        for language, icon_name in reversed([
            ("en", "flag-gb"),
            ("de", "flag-de"),
            ("fr", "flag-fr"),
            ("es", "flag-es"),
            ("it", "flag-it"),
            ("ja", "flag-jp"),
            # ("", "flag-unknown"),
        ]):
            icon = Image("workspace:res/16/" + icon_name + ".png")
            element = LanguageElement(self, language, icon)
            self.hori_layout.add(element, fill=True)
        self.hori_layout.add_spacer(16)

        element = PlayersElement(self)
        self.hori_layout.add(element, fill=True)

        # for config_key, icon_name in [
        #     ("database_url", "database_url_16"),
        #     ("hol_url", "hol_url_16"),
        #     ("lemonamiga_url", "lemon_url_16"),
        #     ("mobygames_url", "mobygames_url_16"),
        #     ("wikipedia_url", "wikipedia_url_16"),
        # ]:
        #     icon = Image("launcher:res/" + icon_name + ".png")
        #     element = LinkButtonElement(self, config_key, icon)
        #     self.hori_layout.add(element)

        element = WebLinkElement(self)
        self.hori_layout.add(element, fill=True)

        # this listener is added after all status bar children have
        # added their listeners, this is important for re-layout...
        LauncherConfig.add_listener(self)

    def on_destroy(self):
        LauncherConfig.remove_listener(self)

    def on_config(self, key, value):
        unused(value)
        layout = False
        if key in ["languages", "protection"]:
            layout = True
        if layout:
            self.layout.update()

    def on_paint(self):
        dc = self.create_dc()
        size = self.size()
        if Skin.fws():
            dc.draw_rectangle(
                0, 0, size[0], 2, Color(0xe5, 0xe5, 0xe5, 0xff))
            return
        color_1 = Skin.get_background_color()
        if color_1 is not None:
            color_1 = color_1.copy().darken(0.12)
        else:
            color_1 = Color(0x00, 0x00, 0x00, 0x30)
        dc.draw_line(0, 0, size[0], 0, color_1)
        self.draw_background(self, dc, offset=1, height=size[1] - 1)

    @classmethod
    def draw_element_background(cls, widget, dc):
        cls.draw_background(widget, dc)

    @classmethod
    def draw_background(cls, widget, dc, offset=None, height=None):
        size = widget.size()
        if Skin.fws():
            return
        x = 0
        y = 0
        w = size[0]
        h = size[1]
        if offset is not None:
            y += offset
        if height is not None:
            h = height

        color_1 = Skin.get_background_color()
        color_2 = color_1
        # if fsui.System.macosx:
        #     color_1 = Color(0xa7, 0xa7, 0xa7)
        #     color_2 = Color(0xc0, 0xc0, 0xc0)
        if color_1 is not None:
            color_1 = color_1.copy().darken(0.08)
        else:
            color_1 = Color(0x00, 0x00, 0x00, 0x20)
            color_2 = Color(0x00, 0x00, 0x00, 0x00)
        dc.draw_vertical_gradient(x, y, w, h, color_1, color_2)
