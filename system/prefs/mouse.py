from typing import Optional

from fswidgets.widget import Widget
from launcher.i18n import gettext
from launcher.settings.mouse_settings_page import MouseSettingsPage
from system.classes.shellobject import shellObject
from system.classes.windowcache import WindowCache
from system.prefs.components.baseprefswindow import BasePrefsWindow


@shellObject
class Mouse:
    @staticmethod
    def open(**kwargs):
        WindowCache.open(MousePrefsWindow, **kwargs)


class MousePrefsWindow(BasePrefsWindow):
    def __init__(self, parent: Optional[Widget] = None):
        super().__init__(parent, title=gettext("Mouse preferences"))
        self.panel = MouseSettingsPage(self)
        self.layout.add(self.panel, fill=True, expand=True)
