from launcher.i18n import gettext
from launcher.settings.language_settings_page import LanguageSettingsPage
from system.classes.shellobject import shellObject
from system.classes.windowcache import WindowCache
from system.prefs.components.baseprefswindow import BasePrefsWindow


@shellObject
class Locale:
    @staticmethod
    def open(**kwargs):
        WindowCache.open(LocalePrefsWindow, **kwargs)


class LocalePrefsWindow(BasePrefsWindow):
    def __init__(self, parent=None):
        super().__init__(parent, title=gettext("Locale preferences"))
        self.panel = LanguageSettingsPage(self)
        self.layout.add(self.panel, fill=True, expand=True)
