from launcher.i18n import gettext
from launcher.settings.whdload_settings_page import WHDLoadSettingsPage
from launcher.system.prefs.common.baseprefswindow import BasePrefsWindow


class WHDLoadPrefsWindow(BasePrefsWindow):
    def __init__(self, parent):
        super().__init__(parent, title=gettext("WHDLoad preferences"))
        self.panel = WHDLoadSettingsPage(self)
        self.layout.add(self.panel, fill=True, expand=True)
