# from launcher.system.classes.window import Window
from launcher.experimental.flexbox.window import Window


class BasePrefsWindow(Window):
    def __init__(self, parent=None, *, title="", style=None):
        super().__init__(parent, title=title, maximizable=False, style=style)
        self.set_background_color(self.theme.dialog_bgcolor())


class BasePrefsWindow2(Window):
    def __init__(self, title, panel_class, style=None):
        super().__init__(None, title=title, maximizable=False, style=style)
        self.set_background_color(self.theme.dialog_bgcolor())
        self.layout.add(panel_class(self), fill=True, expand=True)
