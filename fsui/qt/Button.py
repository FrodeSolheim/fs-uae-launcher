import warnings

from fsui.qt import QParent, QPushButton, QSignal
from fsui.qt.widget import Widget


class Button(Widget):
    activated = QSignal()

    def __init__(self, parent, label=""):
        super().__init__(parent)
        label = "  " + label + "  "
        self.set_widget(QPushButton(label, QParent(parent)))
        self._widget.clicked.connect(self.__clicked)

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
