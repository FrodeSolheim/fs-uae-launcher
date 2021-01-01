from launcher.system.classes.window import Window


class BasePrefsWindow(Window):
    def __init__(self, parent, *, title=""):
        super().__init__(parent, title=title, maximizable=False)
