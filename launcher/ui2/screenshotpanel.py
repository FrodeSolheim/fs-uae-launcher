from typing import Optional

from fsgamesys.config.configevent import ConfigEvent
from fsui import Color, Image, Panel
from fswidgets.widget import Widget
from launcher.ui.imageloader import ImageLoader, ImageLoaderRequest
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
        self,
        parent: Widget,
        index: int,
        imageLoader: ImageLoader,
        default_image: Optional[Image],
        overlay_image: Optional[Image],
    ) -> None:
        super().__init__(parent)
        self.index = index
        self.image_size = SCREEN_SIZE
        self.set_size(self.image_size)
        self.set_background_color(Color(0x777777))

        self._sha1 = ""
        self._request = None
        self._path = ""
        self.imageLoader = imageLoader
        self.default_image = default_image
        self.overlay_image = overlay_image
        self.image = self.default_image
        ConfigDispatch(self, {sha1_keys[index]: self.__on_sha1_config})

    def get_image_path(self) -> Optional[str]:
        if self._sha1:
            return f"sha1:{self._sha1}"
        else:
            return None

    def __on_image_loaded(self, request: ImageLoaderRequest) -> None:
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
    def on_paint(self) -> None:
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
        width, height = self.getSize()

        if self.image is not None:
            dc.drawScaledImage(self.image, x, y, width, height)
        # dc.draw_image(self.overlay_image, x - 10, y - 10)

    def __on_sha1_config(self, event: ConfigEvent) -> None:
        if event.value != self._sha1:
            self._sha1 = event.value
            self.update_image()

    def update_image(self, force: bool = False) -> None:
        path = self.get_image_path()
        if path != self._path or force:
            self._path = path

            # It is important to set is_cover correctly. Different downloaded
            # sizes are used for covers and screenshots.
            is_cover = self.index < 0

            # FIXME: We specify size here, so the loader can use high-quality
            # resizing and give us a prescaled image. However, if we request
            # as size > thumbnail size, maybe we should just get the original
            # size and let fswidgets scale it up when drawing.
            self._request = self.imageLoader.load_image(
                path,
                size=self.image_size,
                on_load=self.__on_image_loaded,
                is_cover=is_cover,
            )
            self.image = self.default_image
            self.refresh()

    def on_resize(self) -> None:
        super().on_resize()
        self.image_size = self.getSize()
        self.update_image(force=True)
