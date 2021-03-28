from launcher.i18n import gettext
from launcher.settings.scan_settings_page import ScanSettingsPage
from launcher.system.prefs.components.baseprefswindow import BasePrefsWindow


class FileDatabasePrefsWindow(BasePrefsWindow):
    def __init__(self, parent):
        super().__init__(parent, title=gettext("File database preferences"))
        self.panel = ScanSettingsPage(self)
        self.layout.add(self.panel, fill=True, expand=True)
