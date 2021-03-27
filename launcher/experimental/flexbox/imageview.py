from launcher.experimental.flexbox.style import Style
import fsui
from launcher.experimental.flexbox.parentstack import ParentStack


class ImageView(fsui.ImageView):
    def __init__(self, image, *, style=None):
        parent = ParentStack.top()
        super().__init__(parent, image)

        default_style = Style({})
        if style is not None:
            default_style.update(style)
        self.style = default_style

        parent.layout.add(self)
