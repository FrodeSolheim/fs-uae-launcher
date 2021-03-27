from launcher.experimental.flexbox.flexcontainer import FlexContainer
from launcher.experimental.flexbox.label import Label


class NotWorkingWarningPanel(FlexContainer):
    def __init__(self, parent=None):
        super().__init__(
            parent=parent, style={"backgroundColor": "#dddd99", "padding": 20}
        )
        Label(
            "Some or all options on this page have no effect at the moment",
            parent=self,
        )
