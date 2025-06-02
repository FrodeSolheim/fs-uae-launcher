from fsui.qt import QLineEdit
from fsui.qt.signal import Signal, SignalWrapper
from fsui.qt.widget_mixin import WidgetMixin


class TextField(QLineEdit, WidgetMixin):
    changed_signal = Signal()
    activated_signal = Signal()

    def __init__(self, parent, text="", read_only=False):
        QLineEdit.__init__(self, text, parent.get_container())
        # Widget.__init__(self, parent)
        self.init_widget(parent)
        self.setReadOnly(read_only)
        # noinspection PyUnresolvedReferences
        self.textChanged.connect(self.__text_changed)
        # noinspection PyUnresolvedReferences
        self.returnPressed.connect(self.__return_pressed)

        self.changed = SignalWrapper(self, "changed")
        self.activated = SignalWrapper(self, "activated")

    def get_text(self):
        return self.text()

    def set_text(self, text):
        self.setText(text)

    def set_cursor_position(self, position):
        self.setCursorPosition(position)

    def on_changed(self):
        pass

    def __text_changed(self, _):
        self.changed.emit()
        self.on_changed()

    def select_all(self):
        self.selectAll()

    def __return_pressed(self):
        self.activated.emit()


class PasswordField(TextField):
    def __init__(self, parent, text=""):
        TextField.__init__(self, parent, text)
        self.setEchoMode(QLineEdit.EchoMode.Password)
