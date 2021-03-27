from .element import LightElement


class Spacer(LightElement):
    def __init__(self, size, size2=None, horizontal=False):
        LightElement.__init__(self, None)
        if size2 is None:
            if horizontal:
                self.width = size
                self.height = 0
            else:
                self.height = size
                self.width = 0
        else:
            self.width = size
            self.height = size2

    def get_min_size(self):
        return self.width, self.height

    def get_min_width(self):
        return self.width

    def get_min_height(self, width):
        return self.height
