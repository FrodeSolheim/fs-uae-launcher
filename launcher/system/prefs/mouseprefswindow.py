from launcher.i18n import gettext
from launcher.settings.mouse_settings_page import MouseSettingsPage
from launcher.system.prefs.common.baseprefswindow import BasePrefsWindow


class MousePrefsWindow(BasePrefsWindow):
    def __init__(self, parent):
        super().__init__(parent, title=gettext("Mouse preferences"))
        self.panel = MouseSettingsPage(self)
        self.layout.add(self.panel, fill=True, expand=True)
