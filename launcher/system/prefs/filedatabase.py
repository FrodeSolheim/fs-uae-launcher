from launcher.i18n import gettext
from launcher.settings.scan_settings_page import ScanSettingsPage
from launcher.system.classes.shellobject import shellObject
from launcher.system.classes.windowcache import WindowCache
from launcher.system.prefs.components.baseprefswindow import BasePrefsWindow


@shellObject
class FileDatabase:
    @staticmethod
    def open(**kwargs):
        WindowCache.open(FileDatabasePrefsWindow, **kwargs)


class FileDatabasePrefsWindow(BasePrefsWindow):
    def __init__(self, parent=None):
        super().__init__(parent, title=gettext("File database preferences"))
        self.panel = ScanSettingsPage(self)
        self.layout.add(self.panel, fill=True, expand=True)
