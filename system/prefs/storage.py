from fsui import Panel
from launcher.translation import t
from system.classes.shellobject import shellObject
from system.classes.windowcache import WindowCache
from system.prefs.components.baseprefswindow import BasePrefsWindow


@shellObject
class Storage:
    @staticmethod
    def open(**kwargs):
        WindowCache.open(StoragePrefsWindow, **kwargs)


class StoragePrefsWindow(BasePrefsWindow):
    def __init__(self, parent=None):
        super().__init__(parent, title=t("Storage preferences"))
        self.panel = StoragePrefsPanel(self)
        self.layout.add(self.panel, fill=True, expand=True)


class StoragePrefsPanel(Panel):
    def __init__(self, parent):
        super().__init__(parent)
        # FIXME
        self.set_min_size((540, 100))
        self.layout.set_padding(20, 0, 20, 20)
