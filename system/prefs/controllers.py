from typing import Optional

from fsui.qt.toplevelwidget import TopLevelWidget
from fswidgets.widget import Widget
from launcher.i18n import t
from launcher.settings.joystick_settings_page import JoystickSettingsPage
from system.classes.shellobject import ShellObject, ShellOpenArgs, shellObject
from system.classes.windowcache import ShellWindowCache
from system.classes.windowresizehandle import WindowResizeHandle
from system.prefs.components.baseprefswindow import BasePrefsWindow


@shellObject
class Controllers(ShellObject):
    @staticmethod
    def shellOpen(args: ShellOpenArgs) -> None:
        ShellWindowCache.open(args, ControllerPrefsWindow)


class ControllerPrefsWindow(BasePrefsWindow):
    def __init__(self, parent: Optional[Widget] = None):
        # title=t("Controller preferences")
        super().__init__(parent, title=t("Controllers"))
        self.panel = JoystickSettingsPage(self)
        self.layout.add(self.panel, fill=True, expand=True)
        WindowResizeHandle(self)

        # Set some sensible initial size to make sure the controller list is
        # not to narrow and small.
        self.setSize((600, self.get_min_height(600)))
