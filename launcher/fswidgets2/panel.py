from typing import Optional

import fsui
from fsui import Widget
from fswidgets.parentstack import ParentStack
from launcher.fswidgets2.style import Style


class Panel(fsui.Panel):
    def __init__(self, parent: Optional[Widget] = None, *, style=None):
        parent = parent or ParentStack.top()
        super().__init__(parent)
        self.style = Style({}, style)

        backgroundColor = self.style.get("backgroundColor")
        if backgroundColor:
            self.set_background_color(fsui.Color.from_hex(backgroundColor))

        if parent.layout is not None:
            parent.layout.add(self)
