import fsui
from fsui import Widget
from launcher.fswidgets2.parentstack import ParentStack
from launcher.fswidgets2.style import Style


class Panel(fsui.Panel):
    def __init__(self, parent: Widget = None, *, style=None):
        parent = parent or ParentStack.top()
        super().__init__(parent)
        self.style = Style({}, style)

        backgroundColor = self.style.get("backgroundColor")
        if backgroundColor:
            self.set_background_color(fsui.Color.from_hex(backgroundColor))

        parent.layout.add(self)
