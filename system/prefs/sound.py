from launcher.i18n import gettext
from launcher.settings.audio_settings_page import AudioSettingsPage
from system.classes.shellobject import shellObject
from system.classes.windowcache import WindowCache
from system.prefs.components.baseprefswindow import BasePrefsWindow


@shellObject
class Sound:
    @staticmethod
    def open(**kwargs):
        WindowCache.open(SoundPrefsWindow, **kwargs)


class SoundPrefsWindow(BasePrefsWindow):
    def __init__(self, parent=None):
        super().__init__(parent, title=gettext("Sound preferences"))
        self.panel = AudioSettingsPage(self)
        self.layout.add(self.panel, fill=True, expand=True)
