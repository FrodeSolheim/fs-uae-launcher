from fsui import Color, Image, Panel
from launcher.system.classes.configdispatch import ConfigDispatch
from launcher.system.exceptionhandler import exceptionhandler
from launcher.ui2.screenshotpanel import ScreenshotPanel
from launcher.ui.imageloader import ImageLoader

COVER_SIZE = (252, 336)


class FrontCoverPanel(ScreenshotPanel):
    def __init__(self, parent, image_loader):
        super().__init__(parent, -1, image_loader, None, None)
        image_size = COVER_SIZE
        self.set_size(image_size)
        self.set_min_size(image_size)
        self.image_size = image_size
        # self.set_background_color(Color(0x999999))
        self.set_background_color(Color(0xC0C0C0))
        # self.set_background_color(None)

    # FIXME: Why is @exceptionhandler needed on this callback? It is generally
    # not needed on other event handlers..?
    @exceptionhandler
    def on_paint(self):
        dc = self.create_dc()
        x = 0
        y = 0
        if self.image is not None:
            dc.draw_image(self.image, x, y)

    def __on_sha1_config(self, event):
        if event.value != self._sha1:
            self._sha1 = event.value
            self.update_image()
