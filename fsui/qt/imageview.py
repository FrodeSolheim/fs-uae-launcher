from fsui.qt.qparent import QParent
from fsui.qt.qt import QLabel
from fswidgets.widget import Widget


class ImageView(Widget):
    def __init__(self, parent, image, stretch=False):
        super().__init__(parent, QLabel(QParent(parent)))
        self._qwidget.setPixmap(image.qpixmap)
        if stretch:
            self._qwidget.setScaledContents(True)

    def set_image(self, image):
        self._qwidget.setPixmap(image.qpixmap)
