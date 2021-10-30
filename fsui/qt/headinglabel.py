from fsui.qt.label import Label
from fswidgets.widget import Widget


class HeadingLabel(Label):
    def __init__(self, parent: Widget, label: str):
        Label.__init__(self, parent, label)
        font = self.font()
        # font.set_bold(True)
        font.set_weight(500)
        self.set_font(font)
