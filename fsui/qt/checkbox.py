from fsui.qt.qparent import QParent
from fsui.qt.qt import QCheckBox
from fsui.qt.signal import Signal, SignalWrapper
from fsui.qt.widget import Widget


class CheckBox(Widget):
    changed_signal = Signal()

    def __init__(self, parent, text="", check=False):
        # self._widget = QCheckBox(text, parent.get_container())
        super().__init__(parent, QCheckBox(text, QParent(parent)))
        self.changed = SignalWrapper(self, "changed")

        # self.init_widget(parent)
        if check:
            self.setChecked(True)
        # self._widget.stateChanged.connect(self.__state_changed)
        self._qwidget.stateChanged.connect(self.__state_changed)

    def __state_changed(self):
        if not self.changed.inhibit:
            self.on_changed()

    def checked(self):
        return self._qwidget.isChecked()

    def check(self, checked=True):
        self.set_checked(checked)

    # FIXME: Rename: on_change?
    def on_changed(self):
        self.changed.emit()

    def set_checked(self, checked):
        self._qwidget.setChecked(checked)

    def uncheck(self):
        self.set_checked(False)


class HeadingCheckBox(CheckBox):
    def __init__(self, parent, text=""):
        super().__init__(parent, text)
        font = self.get_font()
        font.set_bold(True)
        self.set_font(font)
