import logging

from system.classes.shellobject import ShellObject, ShellOpenArgs, shellObject
from system.classes.windowcache import ShellWindowCache
from system.utilities.updater.updaterwindow import UpdaterWindow

log = logging.getLogger(__name__)


@shellObject
class Updater(ShellObject):
    @staticmethod
    def shellOpen(args: ShellOpenArgs) -> None:
        updaterWindow = ShellWindowCache.open(args, UpdaterWindow)
        if updaterWindow.checkForUpdatesButton.isEnabled():
            updaterWindow.checkForUpdates()
