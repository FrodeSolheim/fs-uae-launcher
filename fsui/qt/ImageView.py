import fsui.qt
from .Widget import Widget


class ImageView(Widget):

    def __init__(self, parent, image):
        self._widget = fsui.qt.QLabel(parent.get_container())
        # Widget.__init__(self, parent)
        self.init_widget(parent)
        self._widget.setPixmap(image.qpixmap)

    def set_image(self, image):
        self._widget.setPixmap(image.qpixmap)
