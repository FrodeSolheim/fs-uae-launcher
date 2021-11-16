from typing import Callable, Optional, cast

from fsui.context import get_theme
from fsui.qt.icon import Icon
from fsui.qt.qparent import QParent
from fsui.qt.qt import QFontMetrics, QPushButton, QSignal
from fswidgets.widget import Widget


class Button(Widget):
    activated = QSignal()

    def __init__(
        self,
        parent: Widget,
        label: str = "",
        *,
        icon: Optional[Icon] = None,
        onClick: Optional[Callable[[], None]] = None
    ) -> None:
        if icon:
            qwidget = QPushButton(icon.qicon(), label, QParent(parent))
        else:
            qwidget = QPushButton(label, QParent(parent))
        super().__init__(parent, qwidget)
        self.qPushButton.clicked.connect(self.__on_clicked)

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

    def __on_clicked(self) -> None:
        self.on_activate()

    def on_activate(self) -> None:
        self.activated.emit()

    @property
    def qPushButton(self) -> QPushButton:
        return cast(QPushButton, self.qWidget)
