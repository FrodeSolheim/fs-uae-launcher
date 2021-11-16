from typing import Any, Optional

from fsui import Color
from fsui.qt.toplevelwidget import TopLevelWidget
from launcher.fswidgets2.flexlayout import FlexLayout
from launcher.fswidgets2.style import Style, StyleParam
from system.classes.window import Window as BaseWindow


class Window(BaseWindow):
    def __init__(
        self,
        parent: Optional[TopLevelWidget] = None,
        *args: Any,
        style: Optional[StyleParam] = None,
        **kwargs: Any
    ):
        super().__init__(parent=parent, *args, **kwargs)

        self.style = Style({"flexDirection": "column"}, style)

        backgroundColor = self.style.get("backgroundColor")
        if backgroundColor is not None:
            self.set_background_color(Color.from_hex(backgroundColor))

        flex_layout = FlexLayout(self)
        for child in self.layout.children:
            flex_layout.add(child.element)
        self.layout = flex_layout
