from launcher.i18n import gettext
from launcher.settings.joystick_settings_page import JoystickSettingsPage
from launcher.system.classes.shellobject import shellObject
from launcher.system.classes.windowcache import WindowCache
from launcher.system.prefs.components.baseprefswindow import BasePrefsWindow


@shellObject
class Controller:
    @staticmethod
    def open(**kwargs):
        WindowCache.open(ControllerPrefsWindow, **kwargs)


class ControllerPrefsWindow(BasePrefsWindow):
    def __init__(self, parent=None):
        super().__init__(parent, title=gettext("Controller preferences"))
        self.panel = JoystickSettingsPage(self)
        self.layout.add(self.panel, fill=True, expand=True)
