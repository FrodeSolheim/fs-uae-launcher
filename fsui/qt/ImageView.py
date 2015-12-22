import fsui.qt
from .widget_mixin import WidgetMixin


class ImageView(fsui.qt.QLabel, WidgetMixin):

    def __init__(self, parent, image):
        fsui.qt.QLabel.__init__(self, parent.get_container())
        self.init_widget(parent)
        self.setPixmap(image.qpixmap)

    def set_image(self, image):
        self.setPixmap(image.qpixmap)
