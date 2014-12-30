import fsui.qt
from .Widget import Widget


class ImageButton(fsui.qt.QPushButton, Widget):

    activated = fsui.qt.QSignal()

    def __init__(self, parent, image):
        fsui.qt.QPushButton.__init__(self, parent.get_container())
        self.init_widget(parent)
        self.setIcon(image.qicon)
        self.clicked.connect(self.__clicked)

    def set_image(self, image):
        self.setIcon(image.qicon)

    def __clicked(self):
        self.on_activate()
        self.activated.emit()

    def on_activate(self):
        pass
