import logging
from typing import Any, Dict, Optional

from fsui import Window
from launcher.fswidgets2.window import Window
from system.classes.windowcache import WindowCache
from system.utilities.updater.updaterwindow import UpdaterWindow

log = logging.getLogger(__name__)


def wsopen(window: Optional[Window] = None, **kwargs: Dict[str, Any]):
    return Updater.open(window, **kwargs)


class Updater:
    @staticmethod
    def open(window: Optional[Window] = None, **kwargs: Dict[str, Any]):
        updaterWindow = WindowCache.open(UpdaterWindow, centerOnWindow=window)
        if updaterWindow.checkForUpdatesButton.isEnabled():
            updaterWindow.checkForUpdates()
        return updaterWindow
