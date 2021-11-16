from typing import cast

from fsui.context import get_theme
from fsui.qt.qparent import QParent
from fsui.qt.qt import QFontMetrics, QSpinBox
from fsui.qt.signal import Signal, SignalWrapper
from fswidgets.widget import Widget


class SpinCtrl(Widget):
    changed_signal = Signal()

    def __init__(
        self,
        parent: Widget,
        min_value: int,
        max_value: int,
        initial_value: int,
    ) -> None:
        super().__init__(parent, QSpinBox(QParent(parent)))
        self.qSpinBox.setRange(min_value, max_value)
        self.qSpinBox.setValue(initial_value)
        self.qSpinBox.valueChanged.connect(self.__value_changed)
        # FIXME: What did this to, again?
        self.changed = SignalWrapper(self, "changed")
        self.update_style()

    def get_value(self) -> int:
        return self.qSpinBox.value()

    def on_change(self) -> None:
        self.changed.emit()

    @property
    def qSpinBox(self) -> QSpinBox:
        return cast(QSpinBox, self._qwidget)

    def set_value(self, value: int) -> None:
        self.qSpinBox.setValue(value)

    def update_style(self) -> None:
        theme = get_theme(self)
        padding = theme.textfield_padding()
        if not padding:
            # Indicates that we do not want custom styling
            return
        # There seems to be an issue with specifying padding-top and
        # padding-bottom for a QSpinBox.
        fontmetrics = QFontMetrics(self._widget.font())
        fontheight = fontmetrics.height()
        print(fontheight)
        border = 4
        min_height = fontheight + padding.top + padding.bottom + border
        self.set_min_height(min_height)
        print("MINHEIGHT (SPINCTRL)", min_height)
        # FIXME: This widget seems to have some margin error, the border is
        # drawn so that the widget height is two less than it should be. May
        # need to draw own border in order to get this right! (Sigh)
        self.qSpinBox.setStyleSheet(
            f"""
            QSpinBox {{
                /*
                border: 0;
                margin: 0px;
                */
                /*
                padding-top: 2px;
                padding-bottom: 2px;
                */
                padding-right: {padding.right}px;
                padding-left: {padding.left}px;
            }}
            """
        )

    def __value_changed(self, _: int) -> None:
        if not self.changed.inhibit:
            self.on_changed()
