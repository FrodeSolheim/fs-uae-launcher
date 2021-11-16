from typing import Optional

import fsui
from fswidgets.parentstack import ParentStack
from launcher.fswidgets2.style import Style, StyleParam


class Spacer(fsui.Panel):
    def __init__(
        self, size: int = 20, *, style: Optional[StyleParam] = None
    ) -> None:
        parent = ParentStack.top()
        super().__init__(parent)

        default_style = Style({})
        if style is not None:
            default_style.update(style)
        self.style = default_style

        if parent.layout is not None:
            parent.layout.add(self)
