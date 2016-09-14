import fsui.qt
from .widget_mixin import WidgetMixin


class ImageButton(fsui.qt.QPushButton, WidgetMixin):

    activated = fsui.qt.QSignal()

    def __init__(self, parent, image):
        fsui.qt.QPushButton.__init__(self, parent.get_container())
        self.init_widget(parent)
        icon = image.qicon
        self.setIcon(icon)
        self.setIconSize(fsui.qt.QSize(image.size[0], image.size[1]))
        self.clicked.connect(self.__clicked)

    def set_image(self, image):
        self.setIcon(image.qicon)

    def __clicked(self):
        self.on_activate()
        self.activated.emit()

    def on_activate(self):
        pass
