from launcher.i18n import gettext
from launcher.settings.joystick_settings_page import JoystickSettingsPage
from launcher.system.prefs.baseprefswindow import BasePrefsWindow


class ControllerPrefsWindow(BasePrefsWindow):
    def __init__(self, parent):
        super().__init__(parent, title=gettext("Controller preferences"))
        self.panel = JoystickSettingsPage(self)
        self.layout.add(self.panel, fill=True, expand=True)
