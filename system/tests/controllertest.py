from launcher.controllertest.ControllerTestWindow import ControllerTestWindow
from system.classes.shellobject import ShellObject, ShellOpenArgs, shellObject
from system.classes.windowcache import ShellWindowCache


@shellObject
class ControllerTest(ShellObject):
    # FIXME: Get rid of kwargs
    @staticmethod
    def shellOpen(args: ShellOpenArgs) -> None:
        ShellWindowCache.open(args, ControllerTestWindow)
