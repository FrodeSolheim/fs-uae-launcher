from launcher.system.classes.window import Window as BaseWindow
from launcher.experimental.flexbox.flexlayout import FlexLayout
from launcher.experimental.flexbox.style import Style
from fsui import Color


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
