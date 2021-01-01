from fsui import ImageButton, Image


class IconButton(ImageButton):
    BUTTON_WIDTH = 40

    def __init__(self, parent, name):
        image = Image("launcher:res/" + name)
        ImageButton.__init__(self, parent, image)
        self.set_min_width(self.BUTTON_WIDTH)

    def set_icon_name(self, name):
        image = Image("launcher:res/" + name)
        self.set_image(image)
