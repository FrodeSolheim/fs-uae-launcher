from fsgamesys.options.constants import WORKSPACE_WINDOW_TITLE
from fsui import Panel
from launcher.i18n import gettext
from system.classes.shellobject import shellObject
from system.classes.windowcache import WindowCache
from system.prefs.components.baseprefspanel import BasePrefsPanel
from system.prefs.components.baseprefswindow import BasePrefsWindow


@shellObject
class Workspace:
    @staticmethod
    def open(**kwargs):
        WindowCache.open(WorkspacePrefsWindow, **kwargs)


class WorkspacePrefsWindow(BasePrefsWindow):
    def __init__(self, parent=None):
        super().__init__(parent, title=gettext("Workspace preferences"))
        self.panel = WorkspacePrefsPanel(self)
        self.layout.add(self.panel, fill=True, expand=True)


class WorkspacePrefsPanel(BasePrefsPanel):
    def __init__(self, parent):
        super().__init__(parent)
        # FIXME
        self.set_min_size((540, 100))
        self.layout.set_padding(20, 0, 20, 20)

        self.add_option(WORKSPACE_WINDOW_TITLE)
