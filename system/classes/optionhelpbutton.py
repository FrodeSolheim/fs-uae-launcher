from fswidgets.widget import Widget
from launcher.ui.HelpButton import HelpButton


class OptionHelpButton(HelpButton):
    def __init__(self, parent: Widget, option_name: str) -> None:
        option_url = "https://fs-uae.net/docs/options/" + option_name.replace(
            "_", "-"
        )
        super().__init__(parent, option_url)
