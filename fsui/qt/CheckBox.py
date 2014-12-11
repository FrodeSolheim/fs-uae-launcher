from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from fsui.qt import QCheckBox, Signal
from .Widget import Widget


class CheckBox(QCheckBox, Widget):

    changed = Signal()

    def __init__(self, parent, text=""):
        #self._widget = QCheckBox(text, parent.get_container())
        QCheckBox.__init__(self, text, parent.get_container())
        #Widget.__init__(self, parent)
        self.init_widget(parent)
        #self._widget.stateChanged.connect(self.__state_changed)
        self.stateChanged.connect(self.__state_changed)

    def __state_changed(self):
        self.changed.emit()
        self.on_change()

    def is_checked(self):
        return self.isChecked()

    def check(self, checked=True):
        self.setChecked(checked)

    def on_change(self):
        pass


class HeadingCheckBox(CheckBox):

    def __init__(self, parent, text=""):
        CheckBox.__init__(self, parent, text)
        font = self.get_font()
        font.set_bold(True)
        self.set_font(font)
