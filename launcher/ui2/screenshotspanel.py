from fsui import Color, Image, Panel
from launcher.system.classes.configdispatch import ConfigDispatch
from launcher.ui.imageloader import ImageLoader
from launcher.system.exceptionhandler import exceptionhandler
from launcher.ui2.screenshotpanel import ScreenshotPanel
from fsui.context import get_window


class ScreenshotsPanel(Panel):
    def __init__(self, parent):
        super().__init__(parent)
        self.set_min_height(10 + 150 + 10)
        # self.image_loader = ImageLoader()
        # default_image = Image("launcher:res/screenshot.png")
        # default_image.resize(SCREEN_SIZE)
        default_image = None
        overlay_image = Image("launcher:res/screenshot_overlay.png")
        image_loader = get_window(self).image_loader

        self.screenshotpanels = []
        x = 20
        y = 10
        for i in range(6):
            panel = ScreenshotPanel(
                self, i, image_loader, default_image, overlay_image
            )
            panel.set_position((x, y))
            self.screenshotpanels.append(panel)
            x += panel.width() + 20

    def on_destroy(self):
        # self.image_loader.stop()
        super().on_destroy()
