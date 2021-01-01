from launcher.i18n import gettext
from launcher.settings.language_settings_page import LanguageSettingsPage
from launcher.system.prefs.baseprefswindow import BasePrefsWindow


class LocalePrefsWindow(BasePrefsWindow):
    def __init__(self, parent):
        super().__init__(parent, title=gettext("Locale preferences"))
        self.panel = LanguageSettingsPage(self)
        self.layout.add(self.panel, fill=True, expand=True)
