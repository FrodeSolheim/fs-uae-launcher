import fsui
from launcher.i18n import gettext
from .netplay_panel import NetplayPanel


class NetplayDialog(fsui.Window):
    """Net play window. Max one window of this class should be open."""

    @classmethod
    def open(cls, parent=None):
        return fsui.open_window_instance(cls, parent)

    def __init__(self, parent=None):
        super().__init__(
                parent, "{} - FS-UAE Launcher".format(gettext("Net Play")))
        self.layout = fsui.VerticalLayout()
        self.panel = NetplayPanel(self, header=False)
        self.layout.add(self.panel, expand=True, fill=True)

        self.panel.set_min_size((800, 500))
        self.panel.on_show()
