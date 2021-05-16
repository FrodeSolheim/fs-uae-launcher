import fsui
from fsui import Widget
from fswidgets.parentstack import ParentStack
from launcher.fswidgets2.style import Style


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

    def appendLine(self, text: str):
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
