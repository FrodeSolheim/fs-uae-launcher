from typing import Optional

import fsui
from fsui import Widget
from fswidgets.parentstack import ParentStack
from launcher.fswidgets2.style import Style, StyleParam


class TextArea(fsui.TextArea):
    def __init__(
        self,
        parent: Optional[Widget] = None,
        text: str = "",
        *,
        readOnly: bool = False,
        style: Optional[StyleParam] = None
    ):
        parent = parent or ParentStack.top()
        super().__init__(parent, text, read_only=readOnly)
        self.style = Style({}, style)

        if parent.layout is not None:
            parent.layout.add(self)

    def appendLine(self, text: str):
        self.append_text(text.rstrip("\n"))
        # else:
        #     self.appendText(f"{text}\n")

    # def appendText(self, text):
    #     self.append_text(text)

    def get_min_width(self) -> int:
        return 100

    def get_min_height(self, width: int) -> int:
        return 100

    # def get_min_height(self, width):
    #     # FIXME
    #     return 30
