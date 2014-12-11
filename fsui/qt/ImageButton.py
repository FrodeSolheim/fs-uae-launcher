from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from fsui.qt import QPushButton, QSignal
from .Widget import Widget


class ImageButton(QPushButton, Widget):

    activated = QSignal()

    def __init__(self, parent, image):
        QPushButton.__init__(self, parent.get_container())
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
