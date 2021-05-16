from typing import Any, Dict, Optional

from fswidgets.widget import Widget
from launcher.fswidgets2.window import Window
from launcher.i18n import t
from launcher.settings.joystick_settings_page import JoystickSettingsPage
from system.classes.shellobject import shellObject
from system.classes.windowcache import WindowCache
from system.classes.windowresizehandle import WindowResizeHandle
from system.prefs.components.baseprefswindow import BasePrefsWindow


@shellObject
class Controller:
    @staticmethod
    def open(window: Optional[Window] = None, **kwargs: Dict[str, Any]):
        return WindowCache.open(ControllerPrefsWindow, centerOnWindow=window)


class ControllerPrefsWindow(BasePrefsWindow):
    def __init__(self, parent: Optional[Widget] = None):
        super().__init__(parent, title=t("Controller preferences"))
        self.panel = JoystickSettingsPage(self)
        self.layout.add(self.panel, fill=True, expand=True)
        WindowResizeHandle(self)

        # Set some sensible initial size to make sure the controller list is
        # not to narrow and small.
        self.setSize((600, self.get_min_height(600)))
