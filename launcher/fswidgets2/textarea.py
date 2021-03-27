from launcher.experimental.flexbox.style import Style
import fsui
from launcher.experimental.flexbox.parentstack import ParentStack
from fsui import Widget


class TextArea(fsui.TextArea):
    def __init__(
        self,
        parent: Widget = None,
        text="",
        *,
        readOnly: bool = False,
        style=None
    ):
        parent = parent or ParentStack.top()
        super().__init__(parent, text, read_only=readOnly)
        self.style = Style({}, style)

        parent.layout.add(self)

    def appendLine(self, text):
        self.append_text(text.rstrip("\n"))
        # else:
        #     self.appendText(f"{text}\n")

    # def appendText(self, text):
    #     self.append_text(text)

    def get_min_width(self):
        return 100

    def get_min_height(self, width):
        return 100

    # def get_min_height(self, width):
    #     # FIXME
    #     return 30
