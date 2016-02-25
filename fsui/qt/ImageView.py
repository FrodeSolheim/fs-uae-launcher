import fsui.qt
from .widget_mixin import WidgetMixin


class ImageView(fsui.qt.QLabel, WidgetMixin):

    def __init__(self, parent, image, stretch=False):
        fsui.qt.QLabel.__init__(self, parent.get_container())
        self.init_widget(parent)
        self.setPixmap(image.qpixmap)
        if stretch:
            self.setScaledContents(True)

    def set_image(self, image):
        self.setPixmap(image.qpixmap)
