from launcher.i18n import t
from launcher.settings.joystick_settings_page import JoystickSettingsPage
from system.classes.shellobject import shellObject
from system.classes.windowcache import WindowCache
from system.classes.windowresizehandle import WindowResizeHandle
from system.prefs.components.baseprefswindow import BasePrefsWindow


@shellObject
class Controller:
    @staticmethod
    def open(**kwargs):
        WindowCache.open(ControllerPrefsWindow, **kwargs)


class ControllerPrefsWindow(BasePrefsWindow):
    def __init__(self, parent=None):
        super().__init__(parent, title=t("Controller preferences"))
        self.panel = JoystickSettingsPage(self)
        self.layout.add(self.panel, fill=True, expand=True)
        WindowResizeHandle(self)

        # Set some sensible initial size to make sure the controller list is
        # not to narrow and small.
        self.set_size((600, self.get_min_height(600)))
