from fsui import Color
from launcher.fswidgets2.flexlayout import FlexLayout
from launcher.fswidgets2.style import Style
from system.classes.window import Window as BaseWindow


class Window(BaseWindow):
    def __init__(self, parent=None, *args, style=None, **kwargs):
        super().__init__(parent=parent, *args, **kwargs)

        self.style = Style({"flexDirection": "column"}, style)

        backgroundColor = self.style.get("backgroundColor")
        if backgroundColor is not None:
            self.set_background_color(Color.from_hex(backgroundColor))

        flex_layout = FlexLayout(self)
        for child in self.layout.children:
            flex_layout.add(child.element)
        self.layout = flex_layout
