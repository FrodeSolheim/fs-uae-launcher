from launcher.fswidgets2.flexcontainer import FlexContainer
from launcher.fswidgets2.label import Label


class PrefsNotWorkingWarningPanel(FlexContainer):
    def __init__(self, parent=None):
        super().__init__(
            parent=parent, style={"backgroundColor": "#dddd99", "padding": 20}
        )
        Label(
            "Some or all options on this page have no effect at the moment",
            parent=self,
        )
