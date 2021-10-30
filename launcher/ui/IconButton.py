from fsui import Image, ImageButton
from fswidgets.widget import Widget


class IconButton(ImageButton):
    BUTTON_WIDTH = 40

    def __init__(self, parent: Widget, name: str):
        image = Image("launcher:/data/" + name)
        super().__init__(parent, image)
        self.set_min_width(self.BUTTON_WIDTH)

    def set_icon_name(self, name: str):
        image = Image("launcher:/data/" + name)
        self.set_image(image)
