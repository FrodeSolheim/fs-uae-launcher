from typing import Any

from launcher.controllertest.ControllerTestWindow import ControllerTestWindow
from system.classes.shellobject import shellObject
from system.classes.windowcache import WindowCache


@shellObject
class ControllerTest:
    # FIXME: Get rid of kwargs
    @staticmethod
    def open(**kwargs: Any) -> None:
        WindowCache.open(ControllerTestWindow)
