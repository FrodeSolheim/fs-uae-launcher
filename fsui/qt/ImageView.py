from fsui.qt.helpers import QParent
from fsui.qt.qt import QLabel
from fsui.qt.widget import Widget


class ImageView(Widget):
    def __init__(self, parent, image, stretch=False):
        super().__init__()
        self.set_widget(QLabel(QParent(parent)))
        self._widget.setPixmap(image.qpixmap)
        if stretch:
            self._widget.setScaledContents(True)

    def set_image(self, image):
        self._widget.setPixmap(image.qpixmap)
