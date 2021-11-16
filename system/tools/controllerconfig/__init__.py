from system.classes.shellobject import ShellObject, ShellOpenArgs, shellObject
from system.classes.windowcache import ShellWindowCache
from system.tools.controllerconfig.controllerconfigwindow import (
    ControllerConfigWindow,
)


@shellObject
class ControllerConfig(ShellObject):
    @staticmethod
    def shellOpen(args: ShellOpenArgs) -> None:
        deviceGuid = args.arguments["GUID"]
        ShellWindowCache.open(
            args,
            ControllerConfigWindow,
            {"deviceGuid": deviceGuid},
            cacheKey=(ControllerConfigWindow, deviceGuid),
        )
