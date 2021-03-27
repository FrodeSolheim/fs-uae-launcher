from fscore.observable import Disposer, isObservable
from launcher.experimental.flexbox.style import Style
import fsui
from launcher.experimental.flexbox.parentstack import ParentStack


class Spacer(fsui.Panel):
    def __init__(self, size=20, *, style=None):
        parent = ParentStack.top()
        super().__init__(parent)

        default_style = Style({})
        if style is not None:
            default_style.update(style)
        self.style = default_style

        parent.layout.add(self)
