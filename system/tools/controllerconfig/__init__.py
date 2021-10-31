from typing import Any, Dict

from system.classes.shellobject import shellObject
from system.classes.windowcache import WindowCache
from system.tools.controllerconfig.controllerconfigwindow import (
    ControllerConfigWindow,
)


@shellObject
class ControllerConfig:
    @staticmethod
    # FIXME: Get rid of this Any / kwargs
    def open(
        arguments: Dict[str, str], argumentString: str, **kwargs: Any
    ) -> None:
        print("")
        print("")
        print("")
        print("")
        print(repr(kwargs))
        print(argumentString)
        print(arguments)
        deviceGuid = arguments["GUID"]
        # FIXME: Cache key must include argument as well!
        kwargs["deviceGuid"] = deviceGuid
        WindowCache.open(
            ControllerConfigWindow, {"deviceGuid": deviceGuid}, **kwargs
        )
