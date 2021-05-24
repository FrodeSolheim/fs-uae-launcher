from dataclasses import dataclass
from typing import Literal, Optional


@dataclass
class InputDevice:
    type: Literal["none", "keyboard", "mouse", "joystick"]
    id: str
    name: str
    buttonCount: int = 0
    axisCount: int = 0
    ballCount: int = 0
    hatCount: int = 0
    # FIXME: Or nothing?
    sdl2Name: str = ""
    sdl2ControllerName: str = ""
    # FIXME: sdl2Guuid ?
    sdl2Uuid: str = ""

    # FIXME: Deprecated - used by DeviceManager
    port: Optional[int] = None
