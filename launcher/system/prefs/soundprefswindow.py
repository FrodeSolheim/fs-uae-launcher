from launcher.i18n import gettext
from launcher.settings.audio_settings_page import AudioSettingsPage
from launcher.system.prefs.common.baseprefswindow import BasePrefsWindow


class SoundPrefsWindow(BasePrefsWindow):
    def __init__(self, parent):
        super().__init__(parent, title=gettext("Sound preferences"))
        self.panel = AudioSettingsPage(self)
        self.layout.add(self.panel, fill=True, expand=True)
