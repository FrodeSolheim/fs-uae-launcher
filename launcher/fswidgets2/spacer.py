import fsui
from fscore.observable import Disposer, isObservable
from launcher.fswidgets2.parentstack import ParentStack
from launcher.fswidgets2.style import Style


class Spacer(fsui.Panel):
    def __init__(self, size=20, *, style=None):
        parent = ParentStack.top()
        super().__init__(parent)

        default_style = Style({})
        if style is not None:
            default_style.update(style)
        self.style = default_style

        parent.layout.add(self)
