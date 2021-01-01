from fsui import Panel
from launcher.i18n import gettext
from launcher.system.prefs.baseprefswindow import BasePrefsWindow


class DirectoryPrefsWindow(BasePrefsWindow):
    def __init__(self, parent):
        super().__init__(parent, title=gettext("Directory preferences"))
        self.panel = DirectoryPrefsPanel(self)
        self.layout.add(self.panel, fill=True, expand=True)


class DirectoryPrefsPanel(Panel):
    def __init__(self, parent):
        super().__init__(parent)
        # FIXME
        self.set_min_size((540, 100))
        self.layout.set_padding(20, 0, 20, 20)
