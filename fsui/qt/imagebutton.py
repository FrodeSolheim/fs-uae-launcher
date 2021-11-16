from typing import cast

from fsui.context import get_theme
from fsui.qt.image import Image
from fsui.qt.qparent import QParent
from fsui.qt.qt import QFontMetrics, QPushButton, QSignal, QSize
from fswidgets.widget import Widget


class ImageButton(Widget):
    activated = QSignal()

    def __init__(self, parent: Widget, image: Image) -> None:
        super().__init__(parent, QPushButton(QParent(parent)))
        # if image is not None:
        icon = image.qicon
        self.qPushButton.setIcon(icon)
        self.qPushButton.setIconSize(QSize(image.size[0], image.size[1]))
        self.qPushButton.clicked.connect(self.__clicked)

        theme = get_theme(self)
        padding = theme.button_padding()
        print("THEME", theme, "PADDING", padding)
        if padding is not None:
            fontmetrics = QFontMetrics(self.qPushButton.font())
            fontheight = fontmetrics.height()
            print(fontheight)
            border = 4
            min_height = fontheight + padding.top + padding.bottom + border
            self.set_min_height(min_height)
            print("BUTTONTHEME", theme, min_height)

    @property
    def qPushButton(self) -> QPushButton:
        return cast(QPushButton, self.qWidget)

    def set_image(self, image: Image) -> None:
        self.qPushButton.setIcon(image.qicon)

    def __clicked(self) -> None:
        self.on_activate()

    def on_activate(self) -> None:
        self.activated.emit()
