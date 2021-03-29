from fsui import Color, Image, Panel
from launcher.ui.imageloader import ImageLoader
from system.classes.configdispatch import ConfigDispatch
from system.exceptionhandler import exceptionhandler

# SCREEN_SIZE = (210, 134)
SCREEN_SIZE = (200, 150)
sha1_keys = {
    -1: "front_sha1",
    0: "title_sha1",
    1: "screen1_sha1",
    2: "screen2_sha1",
    3: "screen3_sha1",
    4: "screen4_sha1",
    5: "screen5_sha1",
}


class ScreenshotPanel(Panel):
    def __init__(
        self, parent, index, image_loader, default_image, overlay_image
    ):
        super().__init__(parent)
        self.index = index
        self.image_size = SCREEN_SIZE
        self.set_size(self.image_size)
        self.set_background_color(Color(0x777777))

        self._sha1 = ""
        self._request = None
        self._path = ""
        self.image_loader = image_loader
        self.default_image = default_image
        self.overlay_image = overlay_image
        self.image = self.default_image
        ConfigDispatch(self, {sha1_keys[index]: self.__on_sha1_config})

    def get_image_path(self):
        if self._sha1:
            return f"sha1:{self._sha1}"

    def __on_image_loaded(self, request):
        # print("on_load, request.image =", request.image)
        # if request.path != self.image_paths[request.args["index"]]:
        #     return
        if request.path != self._path:
            return

        if request.image:
            # self.images[request.args["index"]] = request.image
            self.image = request.image
        else:
            # self.images[request.args["index"]] = self.default_image
            self.image = self.default_image
        self.refresh()

    # FIXME: Why is @exceptionhandler needed on this callback? It is generally
    # not needed on other event handlers..?
    @exceptionhandler
    def on_paint(self):
        dc = self.create_dc()
        # self.draw_background(dc)
        # size = self.size()

        # y = 2 + 20
        # x = 10 + self.x_offset
        # for i in range(6):
        #     if x >= size[0] - 12:
        #         break
        #     image = self.images[i]
        #     # dc.draw_image(image, x + 1, y + 1, Constants.SCREEN_SIZE[0],
        #     #         Constants.SCREEN_SIZE[1])
        #     dc.draw_image(image, x + 1, y + 1)
        #     dc.draw_image(self.screenshot_overlay, x - 10, y - 10)
        #     x = x + Constants.SCREEN_SIZE[0] + 22
        x = 0
        y = 0

        if self.image is not None:
            dc.draw_image(self.image, x, y)
        # dc.draw_image(self.overlay_image, x - 10, y - 10)

    def __on_sha1_config(self, event):
        if event.value != self._sha1:
            self._sha1 = event.value
            self.update_image()

    def update_image(self):
        path = self.get_image_path()
        if path != self._path:
            self._path = path

            # It is important to set is_cover correctly. Different downloaded
            # sizes are used for covers and screenshots.
            is_cover = self.index < 0

            self._request = self.image_loader.load_image(
                path,
                size=self.image_size,
                on_load=self.__on_image_loaded,
                is_cover=is_cover,
            )
            self.image = self.default_image
            self.refresh()
