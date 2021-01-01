from launcher.i18n import gettext
from launcher.settings.video_settings_page import VideoSettingsPage
from launcher.system.prefs.baseprefswindow import BasePrefsWindow


class VideoPrefsWindow(BasePrefsWindow):
    def __init__(self, parent):
        super().__init__(parent, title=gettext("Video preferences"))
        self.panel = VideoSettingsPage(self)
        self.layout.add(self.panel, fill=True, expand=True)
