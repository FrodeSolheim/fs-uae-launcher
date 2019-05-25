from fsui.qt.qt import init_qt
from fsbc.application import Application as FSBCApplication


class Application(FSBCApplication):
    def __init__(self, name):
        super().__init__(name)
        self.qapplication = init_qt()
        self.on_create()

    def on_create(self):
        pass

    def run(self):
        self.qapplication.exec_()
        self.stop()

    def set_icon(self, icon):
        self.qapplication.setWindowIcon(icon.qicon())

    def run_in_main(self, function, *args, **kwargs):
        from fsui.qt import call_after

        call_after(function, *args, **kwargs)
