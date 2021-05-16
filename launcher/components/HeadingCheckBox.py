from fswidgets.widget import Widget
from fswidgets.checkbox import CheckBox


class HeadingCheckBox(CheckBox):
    def __init__(self, parent: Widget, text: str = ""):
        super().__init__(parent, text)
        self.setFont(self.getFont().setBold())
