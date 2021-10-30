from dataclasses import dataclass
from enum import Enum, IntEnum
from typing import Optional


class InputDeviceType(Enum):
    KEYBOARD = "KEYBOARD"
    MOUSE = "MOUSE"
    JOYSTICK = "JOYSTICK"


@dataclass
class InputDevice:
    # For all devices
    type: InputDeviceType
    instanceId: str
    name: str

    # For joysticks
    sdlName: str
    sdlGuid: str
    numAxes: int
    numBalls: int
    numButtons: int
    numHats: int

    # _sdlInstanceId: int

    @property
    def id(self) -> str:
        # FIXME: For now
        return self.name

    @property
    def uniqueName(self) -> str:
        # FIXME: For now
        return self.name

    # Temporary fix for DeviceManager
    port: Optional[int] = None


class HatState(IntEnum):
    CENTERED = 0
    UP = 1
    RIGHT = 2
    DOWN = 4
    LEFT = 8
    RIGHTUP = 3
    RIGHTDOWN = 6
    LEFTUP = 9
    LEFTDOWN = 12


# class JoystickState:
class InputDeviceState:
    def __init__(
        self,
        numAxes: int,
        numBalls: int,
        numButtons: int,
        numHats: int,
        *,
        copyFrom: Optional["InputDeviceState"] = None,
    ) -> None:
        if copyFrom is not None:
            # FIXME: mypy has problems understanding this (why?)
            self.axes = copyFrom.axes.copy()  # type: ignore
            self.balls = copyFrom.balls.copy()  # type: ignore
            self.buttons = copyFrom.buttons.copy()  # type: ignore
            self.hats = copyFrom.hats.copy()  # type: ignore
        else:
            self.axes = [0.0 for _ in range(numAxes)]
            self.balls = [0 for _ in range(numBalls)]
            self.buttons = [0 for _ in range(numButtons)]
            self.hats = [HatState.CENTERED for _ in range(numHats)]

    def copy(self) -> "InputDeviceState":
        return InputDeviceState(0, 0, 0, 0, copyFrom=self)

    def __repr__(self) -> str:
        buttonsStr = ", ".join([str(button) for button in self.buttons])
        axesStr = ", ".join([str(axis) for axis in self.axes])
        hatsStr = ", ".join([str(hat) for hat in self.hats])
        itemsStr = ", ".join([x for x in (buttonsStr, axesStr, hatsStr) if x])
        return f"<inputDeviceState {itemsStr}>"


class InputDeviceWithState(InputDevice):
    def __init__(
        self,
        type: InputDeviceType,
        instanceId: str,
        name: str,
        sdlName: str,
        sdlGuid: str,
        numAxes: int,
        numBalls: int,
        numButtons: int,
        numHats: int,
    ) -> None:
        super().__init__(
            type=type,
            instanceId=instanceId,
            name=name,
            sdlName=sdlName,
            sdlGuid=sdlGuid,
            numAxes=numAxes,
            numBalls=numBalls,
            numButtons=numButtons,
            numHats=numHats,
        )
        # self.joystick = JoystickState(numAxes, numBalls, numButtons, numHats)
        self.state = InputDeviceState(numAxes, numBalls, numButtons, numHats)
        self.connected = False

    def getState(self) -> InputDeviceState:
        # stateCopy = InputDeviceState(self.numAxes, self.numBalls)
        return self.state.copy()
