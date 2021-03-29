from launcher.i18n import gettext
from launcher.settings.mouse_settings_page import MouseSettingsPage
from launcher.system.classes.shellobject import shellObject
from launcher.system.classes.windowcache import WindowCache
from launcher.system.prefs.components.baseprefswindow import BasePrefsWindow


@shellObject
class Mouse:
    @staticmethod
    def open(**kwargs):
        WindowCache.open(MousePrefsWindow, **kwargs)


class MousePrefsWindow(BasePrefsWindow):
    def __init__(self, parent=None):
        super().__init__(parent, title=gettext("Mouse preferences"))
        self.panel = MouseSettingsPage(self)
        self.layout.add(self.panel, fill=True, expand=True)
