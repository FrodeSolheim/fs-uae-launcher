from fsui.qt import QPushButton, QSignal
from .widget_mixin import WidgetMixin


class Button(QPushButton, WidgetMixin):

    activated = QSignal()

    def __init__(self, parent, label=""):
        label = "  " + label + "  "
        # self._widget = QPushButton(label, parent.get_container())
        QPushButton.__init__(self, label, parent.get_container())
        # Widget.__init__(self, parent)
        self.init_widget(parent)
        # self._widget.clicked.connect(self.__clicked)
        # if not System.macosx:
        #     self.set_min_height(28)
        self.clicked.connect(self.__clicked)

    def __clicked(self):
        self.on_activated()

    def on_activated(self):
        self.activated.emit()
        # FIXME: Remove
        self.on_activate()

    def on_activate(self):
        pass
