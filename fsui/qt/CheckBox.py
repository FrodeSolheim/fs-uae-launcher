from fsui.qt import QCheckBox, Signal
from .widget_mixin import WidgetMixin


class CheckBox(QCheckBox, WidgetMixin):

    changed = Signal()

    def __init__(self, parent, text="", check=False):
        # self._widget = QCheckBox(text, parent.get_container())
        QCheckBox.__init__(self, text, parent.get_container())
        # Widget.__init__(self, parent)
        self.init_widget(parent)
        if check:
            self.setChecked(True)
        # self._widget.stateChanged.connect(self.__state_changed)
        self.stateChanged.connect(self.__state_changed)

    def __state_changed(self):
        self.changed.emit()
        self.on_changed()

    def is_checked(self):
        return self.isChecked()

    def check(self, checked=True):
        self.setChecked(checked)

    def on_changed(self):
        pass


class HeadingCheckBox(CheckBox):

    def __init__(self, parent, text=""):
        CheckBox.__init__(self, parent, text)
        font = self.get_font()
        font.set_bold(True)
        self.set_font(font)
