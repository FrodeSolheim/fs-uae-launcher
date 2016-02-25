import fsui as fsui
from ...launcher_config import LauncherConfig
from ...launcher_settings import LauncherSettings
from ...game_paths import GamePaths
from .BottomPanel import BottomPanel
from ..Constants import Constants
from ..ImageLoader import ImageLoader
from .RatingButton import RatingButton
from .EditButton import EditButton
from .WebButton import WebButton
from ..Skin import Skin

BORDER = 20


class GameInfoPanel(BottomPanel):

    def __init__(self, parent, cover_on_right=True):
        BottomPanel.__init__(self, parent)
        Skin.set_background_color(self)
        # self.set_background_color((0xdd, 0xdd, 0xdd))

        self.cover_on_right = cover_on_right
        self.requests = None
        self.image = None

        self.layout = fsui.HorizontalLayout()

        # def get_min_height():
        #     return Constants.COVER_SIZE[1] + 2 * BORDER
        # self.layout.get_min_height = get_min_height

        self.layout.padding_left = BORDER // 2
        self.layout.padding_right = BORDER // 2
        self.layout.padding_top = BORDER + 2
        self.layout.padding_bottom = Skin.get_bottom_margin()

        self.default_image = fsui.Image("launcher:res/cover.png")
        # self.default_image.resize(Constants.COVER_SIZE)
        self.cover_overlay = fsui.Image(
            "launcher:res/cover_overlay.png")
        self.cover_overlay_square = fsui.Image(
            "launcher:res/cover_overlay_square.png")

        if not self.cover_on_right:
            self.layout.add_spacer(Constants.COVER_SIZE[0])

        # self.panel = fsui.Panel(self)
        # self.panel.set_background_color((0xdd, 0xdd, 0xdd))
        # self.layout.add(self.panel, expand=True, fill=True)

        vert_layout = fsui.VerticalLayout()
        self.layout.add(vert_layout, expand=True, fill=True)
        # self.panel.layout.padding_top = 10
        if self.cover_on_right:
            vert_layout.padding_right = BORDER
        else:
            vert_layout.padding_left = BORDER

        vert_layout.add_spacer(58 + 3)
        hori_layout = fsui.HorizontalLayout()
        vert_layout.add(hori_layout, fill=True)

        hori_layout.add_spacer(0, expand=True)

        self.web_button = WebButton(self)
        hori_layout.add(self.web_button, margin_right=3)

        self.edit_button = EditButton(self)
        hori_layout.add(self.edit_button, margin_right=3)

        # def label_min_width():
        #     return 330
        # self.title_label = fsui.HeadingLabel(self)
        # self.title_label.get_min_width = label_min_width
        # vert_layout.add(self.title_label)

        # self.sub_title_label = fsui.Label(self)
        # self.sub_title_label.get_min_width = label_min_width
        # vert_layout.add(self.sub_title_label)

        self.title = ""
        self.sub_title = ""
        self.year = ""
        self.publisher = ""
        self.developer = ""
        self.companies = ""

        self.image_path = ""

        vert_layout.add_spacer(0, expand=True)

        hori_layout = fsui.HorizontalLayout()
        vert_layout.add(hori_layout, fill=True)

        # for rating in [1, 4, 5]:
        #     button = RatingButton(self, rating)
        #     hori_layout.add(button, margin_right=5, fill=True)

        hori_layout.add_spacer(0, expand=True)
        # self.launch_group = LaunchGroup(self)
        # hori_layout.add(self.launch_group, fill=True)

        if self.cover_on_right:
            self.layout.add_spacer(Constants.COVER_SIZE[0])

        self.image_loader = ImageLoader()
        self.load_info()
        LauncherSettings.add_listener(self)
        LauncherConfig.add_listener(self)

        for key in ["database_url", "hol_url", "lemon_url", "mobygames_url",
                    "wikipedia_url", "year", "publisher", "developer"]:
            self.on_config(key, LauncherConfig.get(key))

    def on_destroy(self):
        LauncherConfig.remove_listener(self)
        LauncherSettings.remove_listener(self)
        self.image_loader.stop()

    def load_info(self):
        handler = GamePaths.current()
        name = handler.get_name()
        variant = handler.get_variant()
        if variant.startswith("Amiga, "):
            variant = variant[7:]
        self.title = name
        self.sub_title = variant
        self.sub_title = self.sub_title.replace(", ", " \u00b7 ")

        path = handler.get_cover_path()
        if path != self.image_path:
            self.image_path = path

            def on_load(request):
                if request.path != self.image_path:
                    return
                if request.image:
                    self.image = request.image
                else:
                    self.image = self.default_image
                self.image_path = request.path
                self.refresh()

            self.requests = self.image_loader.load_image(
                path, size=Constants.COVER_SIZE, on_load=on_load,
                is_cover=True)
            self.image = self.default_image

        self.refresh()
        self.layout.update()

    def on_setting(self, key, _):
        if key == "parent_uuid":
            self.load_info()
        if key == "config_name":
            self.load_info()

    def on_config(self, key, value):
        if key == "publisher":
            self.publisher = value
            self.update_companies()
        elif key == "developer":
            self.developer = value
            self.update_companies()
        elif key == "year":
            self.year = value

    def update_companies(self):
        companies = [x.strip() for x in self.publisher.split("/") if x.strip()]
        for developer in self.developer.split("/"):
            developer = developer.strip()
            if developer and developer not in companies:
                companies.append(developer)
        self.companies = " \u00b7 ".join(companies)

    def on_paint(self):
        dc = self.create_dc()
        self.draw_background(dc)

        if self.cover_on_right:
            x = self.get_size()[0] - 10 - Constants.COVER_SIZE[0]
            text_x = 10
        else:
            x = 10
            text_x = 10 + Constants.COVER_SIZE[0] + 20

        y = 2 + 20
        size = self.size()

        image = self.image
        # dc.draw_image(image, x, y)
        if image.size[0] == image.size[1]:
            # cover_overlay = self.cover_overlay_square
            y_offset = 14
            # title_x = 10
        else:
            y_offset = 0
        cover_overlay = self.cover_overlay

        if image.size[0] == image.size[1]:
            dc.draw_rectangle(
                x + 1, y + 1, Constants.COVER_SIZE[0],
                Constants.COVER_SIZE[1], fsui.Color(0x0, 0x0, 0x0))
        dc.draw_image(image, x + 1, y + 1 + y_offset)
        dc.draw_image(cover_overlay, x - 10, y - 10)

        font = dc.get_font()
        font.set_bold(True)
        dc.set_font(font)

        dc.draw_text(self.title, text_x, y)
        # tw, th = \
        dc.measure_text(self.title)
        # y += int(th * 1.2)
        y += 24

        color = dc.get_text_color()
        color.mix(self.get_background_color(), 0.33)
        dc.set_text_color(color)

        if self.year:
            twy, thy = dc.measure_text(self.year)
            dc.draw_text(self.year, text_x, y)
            twy += 10
        else:
            twy = 0
        font.set_bold(False)
        dc.set_font(font)
        if self.companies:
            dc.draw_text(self.companies, text_x + twy, y)

        background = fsui.Color(0x00, 0x00, 0x00, 0x20)
        y = 80
        h = 30

        tw, th = dc.measure_text(self.sub_title)
        if self.cover_on_right:
            dc.draw_rectangle(
                text_x, y, size[0] - Constants.COVER_SIZE[0] - 20 - 20, h,
                background)
            dc.draw_text(self.sub_title, text_x + 6, y + (h - th) // 2)
        else:
            dc.draw_rectangle(
                text_x - 18, y, size[0] - text_x + 18, h, background)
            dc.draw_text(self.sub_title, text_x, y + (h - th) // 2)
