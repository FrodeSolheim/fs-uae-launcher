import warnings

import fsui.qt
from .widget_mixin import WidgetMixin
from fsui.qt.widget import Widget
from fsui.qt import QParent, QPushButton, QSignal


class ImageButton(Widget):

    activated = QSignal()

    def __init__(self, parent, image):
        super().__init__(parent)
        self.set_widget(QPushButton(QParent(parent)))
        fsui.qt.QPushButton.__init__(self, parent.get_container())
        icon = image.qicon
        self._widget.setIcon(icon)
        self._widget.setIconSize(fsui.qt.QSize(image.size[0], image.size[1]))
        self._widget.clicked.connect(self.__clicked)

    def set_image(self, image):
        self._widget.setIcon(image.qicon)

    def __clicked(self):
        self.on_activated()

    def on_activated(self):
        self.activated.emit()
        # FIXME: Remove
        self.on_activate()

    def on_activate(self):
        pass

    @property
    def clicked(self):
        warnings.warn("use activated instead", DeprecationWarning)
        return self.activated
