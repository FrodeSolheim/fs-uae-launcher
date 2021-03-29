from launcher.i18n import gettext
from launcher.settings.whdload_settings_page import WHDLoadSettingsPage
from system.classes.shellobject import shellObject
from system.classes.windowcache import WindowCache
from system.prefs.components.baseprefswindow import BasePrefsWindow


@shellObject
class WHDLoad:
    @staticmethod
    def open(**kwargs):
        WindowCache.open(WHDLoadPrefsWindow, **kwargs)


class WHDLoadPrefsWindow(BasePrefsWindow):
    def __init__(self, parent=None):
        super().__init__(parent, title=gettext("WHDLoad preferences"))
        self.panel = WHDLoadSettingsPage(self)
        self.layout.add(self.panel, fill=True, expand=True)
