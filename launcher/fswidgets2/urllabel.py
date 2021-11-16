from typing import Optional

import fsui
from fswidgets.parentstack import ParentStack
from launcher.fswidgets2.style import Style, StyleParam


class UrlLabel(fsui.URLLabel):
    def __init__(
        self,
        text: str = "",
        url: str = "",
        *,
        style: Optional[StyleParam] = None
    ):
        parent = ParentStack.top()
        super().__init__(parent, text, url)

        default_style = Style({})
        if style is not None:
            default_style.update(style)
        self.style = default_style

        if parent.layout is not None:
            parent.layout.add(self)
