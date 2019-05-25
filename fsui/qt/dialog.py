from fsui.qt import Qt, QDialog
from fsui.qt.helpers import QParent
from fsui.qt.windowbase import WindowBase


class Dialog(WindowBase(QDialog)):
    def __init__(self, parent=None, title=""):
        super().__init__(QParent(parent), title=title)

    def __del__(self):
        print("fsui.Dialog.__del__", self)

    def real_window(self):
        return self

    def show_modal(self):
        self.center_on_initial_show()
        # self.setWindowModality(Qt.WindowModal)
        return self.exec_()

    def show(self):
        self.center_on_initial_show()
        self.setWindowModality(Qt.WindowModal)
        return self.exec_()

    def end_modal(self, value):
        self.done(value)
