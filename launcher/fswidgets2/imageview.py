from typing import Optional

import fsui
from fsui.qt.image import Image
from fswidgets.parentstack import ParentStack
from launcher.fswidgets2.style import Style, StyleParam


class ImageView(fsui.ImageView):
    def __init__(self, image: Image, *, style: Optional[StyleParam] = None):
        parent = ParentStack.top()
        super().__init__(parent, image)

        default_style = Style({})
        if style is not None:
            default_style.update(style)
        self.style = default_style

        if parent.layout is not None:
            parent.layout.add(self)
