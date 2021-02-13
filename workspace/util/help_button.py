import workspace
import workspace.ui
from fsbc.desktop import open_url_in_browser


class HelpButton(workspace.ui.ImageButton):
    def __init__(self, parent, url):
        super().__init__(
            parent,
            workspace.ui.Image(
                workspace.Stream(__name__, "data/16x16/information.png")
            ),
        )
        self.url = url
        self.set_min_width(40)

    def on_activate(self):
        open_url_in_browser(self.url)
