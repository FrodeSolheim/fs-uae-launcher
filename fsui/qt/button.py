from fsui.context import get_theme
from fsui.qt.qparent import QParent
from fsui.qt.qt import QFontMetrics, QPushButton, QSignal
from fswidgets.widget import Widget


class Button(Widget):
    activated = QSignal()

    def __init__(self, parent, label="", *, icon=None, onClick=None):
        if icon:
            qwidget = QPushButton(icon.qicon(), label, QParent(parent))
        else:
            qwidget = QPushButton(label, QParent(parent))
        super().__init__(parent, qwidget)
        self._qwidget.clicked.connect(self.__on_clicked)

        theme = get_theme(self)
        padding = theme.button_padding()
        if padding:
            fontmetrics = QFontMetrics(self._widget.font())
            fontheight = fontmetrics.height()
            border = 4
            min_height = fontheight + padding.top + padding.bottom + border
            self.set_min_height(min_height)

        if onClick is not None:
            self.activated.connect(onClick)

    def __on_clicked(self):
        self.on_activate()

    def on_activate(self):
        self.activated.emit()
