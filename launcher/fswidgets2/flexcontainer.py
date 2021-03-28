import fsui
from launcher.fswidgets2.flexlayout import FlexLayout
from launcher.fswidgets2.parentstack import ParentStack
from launcher.fswidgets2.style import Style


class FlexContainer(fsui.Panel):
    def __init__(self, parent=None, *, style=None):
        self.style = Style({"flexDirection": "row"})
        if style is not None:
            self.style.update(style)
        if parent is None:
            parent = ParentStack.top()
        super().__init__(parent)
        self.layout = FlexLayout(self)

        # flex_direction = self.style.get("flexDirection")
        # if flex_direction == "row":
        #     self.layout.direction = 0
        # elif flex_direction == "column":
        #     self.layout.direction = 1
        # else:
        #     raise Exception(f"Unsupported flexDirection {flex_direction}")

        # self.set_background_color(fsui.Color(0xff, 0x99, 0x99))
        backgroundColor = self.style.get("backgroundColor")
        if backgroundColor:
            self.set_background_color(fsui.Color.from_hex(backgroundColor))
        # if isinstance(parent, fsui.Window):
        parent.layout.add(self, fill=True, expand=True)
        # else:
        #     parent.layout.add(self)

    def __enter__(self):
        ParentStack.stack.append(self)

    def __exit__(self, exception_type, exception_value, exception_traceback):
        assert ParentStack.stack.pop() == self


class VerticalFlexContainer(FlexContainer):
    def __init__(self, parent=None, *, style=None):
        default_style = {"flexDirection": "column"}
        if style is not None:
            default_style.update(style)
        super().__init__(parent=parent, style=default_style)
