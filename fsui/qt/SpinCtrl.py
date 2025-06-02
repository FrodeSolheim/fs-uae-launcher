from fsui.qt.helpers import QParent
from fsui.qt.qt import QSpinBox
from fsui.qt.signal import Signal, SignalWrapper
from fsui.qt.widget import Widget


class SpinCtrl(Widget):
    _widget: QSpinBox

    changed_signal = Signal()

    def __init__(self, parent, min_value, max_value, initial_value):
        super().__init__(parent)
        self.set_widget(QSpinBox(QParent(parent)))
        self._widget.setRange(min_value, max_value)
        self._widget.setValue(initial_value)
        self._widget.valueChanged.connect(self.__value_changed)
        self.changed = SignalWrapper(self, "changed")

    def get_value(self):
        return self._widget.value()

    def set_value(self, value):
        self._widget.setValue(value)

    def __value_changed(self, _):
        if not self.changed.inhibit:
            self.on_changed()

    def on_changed(self):
        self.changed.emit()
