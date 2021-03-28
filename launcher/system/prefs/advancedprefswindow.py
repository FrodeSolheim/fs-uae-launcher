from launcher.i18n import gettext
from launcher.settings.advanced_settings_page import AdvancedSettingsPage
from launcher.system.prefs.components.baseprefswindow import BasePrefsWindow


class AdvancedPrefsWindow(BasePrefsWindow):
    def __init__(self, parent):
        super().__init__(parent, title=gettext("Advanced preferences"))
        self.panel = AdvancedSettingsPage(self)
        self.layout.add(self.panel, fill=True, expand=True)
