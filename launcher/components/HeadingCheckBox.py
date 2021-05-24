from fswidgets.checkbox import CheckBox
from fswidgets.widget import Widget


class HeadingCheckBox(CheckBox):
    def __init__(self, parent: Widget, text: str = ""):
        super().__init__(parent, text)
        self.setFont(self.getFont().setBold())
