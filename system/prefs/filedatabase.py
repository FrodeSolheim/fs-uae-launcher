from typing import Any, Optional

from fswidgets.widget import Widget
from launcher.i18n import gettext
from launcher.settings.scan_settings_page import ScanSettingsPage
from system.classes.shellobject import shellObject
from system.classes.windowcache import WindowCache
from system.classes.windowresizehandle import WindowResizeHandle
from system.prefs.components.baseprefswindow import BasePrefsWindow


@shellObject
class FileDatabase:
    @staticmethod
    def open(**kwargs: Any):
        WindowCache.open(FileDatabasePrefsWindow, **kwargs)


class FileDatabasePrefsWindow(BasePrefsWindow):
    def __init__(self, parent: Optional[Widget] = None):
        super().__init__(parent, title=gettext("File database preferences"))
        self.panel = ScanSettingsPage(self)
        self.layout.add(self.panel, fill=True, expand=True)
        WindowResizeHandle(self)

        # Set some sensible initial size to make sure the directory list is
        # not to narrow and small.
        self.set_size((600, 400))
