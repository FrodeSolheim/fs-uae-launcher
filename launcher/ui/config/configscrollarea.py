from fsui import Color, VerticalScrollArea
from fswidgets.widget import Widget

# from fsui.context import get_theme
# from ..skin import Skin


class ConfigScrollArea(VerticalScrollArea):
    def __init__(self, parent: Widget) -> None:
        super().__init__(parent)
        # Skin.set_background_color(self)
        # self.set_background_color(get_theme(self).window_bgcolor())
        # self.set_background_color(Color(0, 255, 0))
        self.set_background_color(Color(0, 0, 0, 0))
