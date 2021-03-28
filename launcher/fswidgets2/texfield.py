import fsui
from launcher.fswidgets2.parentstack import ParentStack
from launcher.fswidgets2.style import Style


class TextField(fsui.TextField):
    def __init__(self, text="", *, type="text", style=None):
        parent = ParentStack.top()
        passwordMode = type == "password"
        super().__init__(parent, text, passwordMode=passwordMode)

        default_style = Style({})
        if style is not None:
            default_style.update(style)
        self.style = default_style

        parent.layout.add(self)

    def get_min_width(self):
        return 100

    # def get_min_height(self, width):
    #     # FIXME
    #     return 30
