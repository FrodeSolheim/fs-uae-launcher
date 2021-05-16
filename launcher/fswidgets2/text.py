import fsui
from fsui import Widget
from fswidgets.parentstack import ParentStack
from launcher.fswidgets2.style import Style


class Text(fsui.MultiLineLabel):
    def __init__(self, text="", *, parent: Widget = None, style=None):
        parent = parent or ParentStack.top()
        super().__init__(parent, text)
        self.style = Style({}, style)

        parent.layout.add(self)

    # Completely override the original get_min_height from MultiLineLabel
    # (for now) since this method is better but *might* be backwards
    # incompatible.
    def get_min_height(self, width):
        height = self._qwidget.heightForWidth(width) + 1
        # if hasattr(self, "min_height"):
        #     return max(self.min_height, height)
        return height
