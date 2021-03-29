from launcher.i18n import gettext
from launcher.settings.advanced_settings_page import AdvancedSettingsPage
from system.classes.shellobject import shellObject
from system.classes.windowcache import WindowCache
from system.prefs.components.baseprefswindow import BasePrefsWindow


@shellObject
class Advanced:
    @staticmethod
    def open(**kwargs):
        WindowCache.open(AdvancedPrefsWindow, **kwargs)


class AdvancedPrefsWindow(BasePrefsWindow):
    def __init__(self, parent=None):
        super().__init__(parent, title=gettext("Advanced preferences"))
        self.panel = AdvancedSettingsPage(self)
        self.layout.add(self.panel, fill=True, expand=True)
