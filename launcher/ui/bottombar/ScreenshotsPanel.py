import fsui
from fsbc.util import unused
from launcher.ui.Constants import Constants
from launcher.ui.imageloader import ImageLoader

from ...game_paths import GamePaths
from ...launcher_settings import LauncherSettings
from ..skin import Skin
from .BottomPanel import BottomPanel

BORDER = 20


class ScreenshotsPanel(BottomPanel):
    def __init__(self, parent):
        BottomPanel.__init__(self, parent)
        Skin.set_background_color(self)
        self.layout = fsui.HorizontalLayout()
        self.image_loader = ImageLoader()

        def get_min_width():
            return 0

        # def get_min_height(width):
        #     return Constants.SCREEN_SIZE[1] + 2 * BORDER
        self.layout.get_min_width = get_min_width
        # self.layout.get_min_height = get_min_height
        self.layout.padding_left = BORDER // 2
        self.layout.padding_right = BORDER // 2
        self.layout.padding_top = BORDER + 2
        self.layout.padding_bottom = Skin.get_bottom_margin()

        self.default_image = fsui.Image("launcher:/data/screenshot.png")
        # self.default_image.resize(Constants.SCREEN_SIZE)
        self.screenshot_overlay = fsui.Image(
            "launcher:/data/screenshot_overlay.png"
        )

        self.images = [self.default_image for _ in range(6)]
        self.image_paths = ["" for _ in range(6)]
        self.requests = [None for _ in range(6)]

        self.x_offset = 0

        self.load_images()
        LauncherSettings.add_listener(self)

    def on_destroy(self):
        LauncherSettings.remove_listener(self)
        self.image_loader.stop()
        super().on_destroy()

    def set_min_screenshots(self, count):
        # w = SCREEN_SIZE[0] * count + BORDER * 2 + (BORDER + 1) * (count - 1)
        w = (
            Constants.SCREEN_SIZE[0] * count
            + BORDER * 2
            + BORDER * (count - 1)
        )
        self.set_min_width(w)

    def load_images(self):
        # t1 = time.time()
        handler = GamePaths.current()
        for i in range(6):
            path = handler.get_screenshot_path(i)
            if path == self.image_paths[i]:
                continue
            self.image_paths[i] = path

            def on_load(request):
                # print("on_load, request.image =", request.image)
                if request.path != self.image_paths[request.args["index"]]:
                    return
                if request.image:
                    self.images[request.args["index"]] = request.image
                else:
                    self.images[request.args["index"]] = self.default_image
                self.refresh()

            self.requests[i] = self.image_loader.load_image(
                path, size=Constants.SCREEN_SIZE, on_load=on_load, index=i
            )
            self.images[i] = self.default_image
            self.refresh()

            # image = handler.load_screenshot_preview(i)
            # if image:
            #     self.images[i] = image
            #     self.refresh()
            # else:
            #     self.images[i] = self.default_image
            #     self.refresh()

        # t2 = time.time()
        # print(t2 - t1)

    def on_setting(self, key, value):
        unused(value)
        if key == "config_name":
            self.x_offset = 0
            self.load_images()
        if key == "parent_uuid":
            self.x_offset = 0
            self.load_images()

    def on_left_down(self):
        # print("on_left_down")
        width = 22 + Constants.SCREEN_SIZE[0] * 6 + 22 * 5
        if self.x_offset == 0:
            self.x_offset = self.size()[0] - width
        else:
            self.x_offset = 0
        self.refresh()

    def on_paint(self):
        dc = self.create_dc()
        self.draw_background(dc)
        size = self.size()

        y = 2 + 20
        x = 10 + self.x_offset
        for i in range(6):
            if x >= size[0] - 12:
                break
            image = self.images[i]
            # dc.draw_image(image, x + 1, y + 1, Constants.SCREEN_SIZE[0],
            #         Constants.SCREEN_SIZE[1])
            dc.draw_image(image, x + 1, y + 1)
            dc.draw_image(self.screenshot_overlay, x - 10, y - 10)
            x = x + Constants.SCREEN_SIZE[0] + 22
