from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from fsui.qt import QLineEdit, Signal
from .Widget import Widget


class TextField(QLineEdit, Widget):

    changed = Signal()
    activated = Signal()

    def __init__(self, parent, text="", read_only=False):
        QLineEdit.__init__(self, text, parent.get_container())
        #Widget.__init__(self, parent)
        self.init_widget(parent)
        self.setReadOnly(read_only)
        self.textChanged.connect(self.__text_changed)
        self.returnPressed.connect(self.__return_pressed)

    def get_text(self):
        return self.text()

    def set_text(self, text):
        self.setText(text)

    def set_cursor_position(self, position):
        self.setCursorPosition(position)

    def on_change(self):
        pass

    def __text_changed(self, text):
        self.changed.emit()
        self.on_change()

    def select_all(self):
        self.selectAll()

    def __return_pressed(self):
        self.activated.emit()


class PasswordField(TextField):

    def __init__(self, parent, text=""):
        TextField.__init__(self, parent, text)
        self.setEchoMode(QLineEdit.Password)
