from launcher.i18n import gettext
from launcher.settings.plugins_settings_page import PluginsSettingsPage
from launcher.system.prefs.baseprefswindow import BasePrefsWindow


class PluginPrefsWindow(BasePrefsWindow):
    def __init__(self, parent):
        super().__init__(parent, title=gettext("Plugin preferences"))
        self.panel = PluginsSettingsPage(self)
        self.layout.add(self.panel, fill=True, expand=True)
