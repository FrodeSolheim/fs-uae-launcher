from typing import List, Optional

from fsui import Image, Panel
from fswidgets.decorators import constructor
from fswidgets.widget import Widget
from launcher.context import useImageLoader
from launcher.ui2.screenshotpanel import ScreenshotPanel


class ScreenshotsPanel(Panel):
    @constructor
    def __init__(self, parent: Widget) -> None:
        super().__init__(parent)
        # self.set_min_height(10 + 150 + 10)
        # self.imageLoader = ImageLoader()
        # default_image = Image("launcher:/data/screenshot.png")
        # default_image.resize(SCREEN_SIZE)
        default_image: Optional[Image] = None
        overlay_image = Image("launcher:/data/screenshot_overlay.png")
        imageLoader = useImageLoader(self)

        self.screenshotpanels: List[ScreenshotPanel] = []
        x = 20
        y = 10
        for i in range(6):
            panel = ScreenshotPanel(
                self, i, imageLoader, default_image, overlay_image
            )
            panel.setPosition((x, y))
            self.screenshotpanels.append(panel)
            x += panel.getWidth() + 20

    def on_resize(self) -> None:
        super().on_resize()
        height = self.getHeight() - 20
        width = (height * 4) // 3
        # print((width, height))
        x = 20
        y = 10
        for panel in self.screenshotpanels:
            # panel.setSize(())
            panel.setPositionAndSize((x, y), (width, height))
            x += panel.getWidth() + 20

    # def onDestroy(self):
    #     super().onDestroy()
    #     self.imageLoader.stop()
