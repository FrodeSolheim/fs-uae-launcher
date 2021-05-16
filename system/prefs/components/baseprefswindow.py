# from system.classes.window import Window
from typing import Optional

from fswidgets.style import Style
from fswidgets.widget import Widget
from launcher.fswidgets2.window import Window


class BasePrefsWindow(Window):
    def __init__(
        self,
        parent: Optional[Widget] = None,
        *,
        title: str = "",
        style: Optional[Style] = None
    ):
        super().__init__(parent, title=title, maximizable=False, style=style)
        self.set_background_color(self.theme.dialog_bgcolor())


class BasePrefsWindow2(Window):
    def __init__(self, title, panel_class, style=None):
        super().__init__(None, title=title, maximizable=False, style=style)
        self.set_background_color(self.theme.dialog_bgcolor())
        self.layout.add(panel_class(self), fill=True, expand=True)
