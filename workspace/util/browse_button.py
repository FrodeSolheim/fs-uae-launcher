import workspace
import workspace.ui


class BrowseButton(workspace.ui.ImageButton):
    def __init__(self, parent, url=""):
        super().__init__(
            parent,
            workspace.ui.Image(
                workspace.Stream(__name__, "data/16/folder.png")
            ),
        )
        self.url = url
        self.set_min_width(40)

    def on_activate(self):
        pass
