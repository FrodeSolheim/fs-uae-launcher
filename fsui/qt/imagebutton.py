from fsui.context import get_theme
from fsui.qt.qparent import QParent
from fsui.qt.qt import QPushButton, QSignal, QSize, QFontMetrics
from fsui.qt.widget import Widget


class ImageButton(Widget):
    activated = QSignal()

    def __init__(self, parent, image):
        super().__init__(parent, QPushButton(QParent(parent)))
        # if image is not None:
        icon = image.qicon
        self._qwidget.setIcon(icon)
        self._qwidget.setIconSize(QSize(image.size[0], image.size[1]))
        self._qwidget.clicked.connect(self.__clicked)

        theme = get_theme(self)
        padding = theme.button_padding()
        print("THEME", theme, "PADDING", padding)
        if padding:
            fontmetrics = QFontMetrics(self._qwidget.font())
            fontheight = fontmetrics.height()
            print(fontheight)
            border = 4
            min_height = fontheight + padding.top + padding.bottom + border
            self.set_min_height(min_height)
            print("BUTTONTHEME", theme, min_height)

    def set_image(self, image):
        self._qwidget.setIcon(image.qicon)

    def __clicked(self):
        self.on_activate()

    def on_activate(self):
        self.activated.emit()
