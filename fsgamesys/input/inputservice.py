import collections
import json
import logging
import subprocess
import threading
from typing import (
    Callable,
    ClassVar,
    Deque,
    Dict,
    List,
    Optional,
    Union,
    cast,
    overload,
)

from typing_extensions import Literal, TypedDict

from fscore.events import Event, EventHelper
from fscore.mainloop import useMainLoop
from fscore.types import SimpleCallable
from fsgamesys.input.gamecontroller import GameControllerMapping
from fsgamesys.input.gamecontrollerdb import useGameControllerDB
from fsgamesys.input.inputdevice import (
    HatState,
    InputDevice,
    InputDeviceType,
    InputDeviceWithState,
)
from fsgamesys.input.legacyconfig import LegacyConfig

log = logging.getLogger(__name__)


class InputServiceEvent(Event):
    pass


class DeviceConnectedEvent(InputServiceEvent):
    type = "deviceconnected"

    def __init__(self, inputDevice: InputDevice):
        self.inputDevice = inputDevice


class DeviceDisconnectedEvent(InputServiceEvent):
    type = "devicedisconnected"

    def __init__(self, inputDevice: InputDevice):
        self.inputDevice = inputDevice


class GamepadConnectedEvent(InputServiceEvent):
    type = "gamepadconnected"

    def __init__(self, inputDevice: InputDevice):
        self.inputDevice = inputDevice


class GamepadDisconnectedEvent(InputServiceEvent):
    type: ClassVar[str] = "gamepaddisconnected"

    def __init__(self, inputDevice: InputDevice):
        self.inputDevice = inputDevice


class JoystickConnectedEvent(InputServiceEvent):
    type = "joystickconnected"

    def __init__(self, inputDevice: InputDevice):
        self.inputDevice = inputDevice


class JoystickDisconnectedEvent(InputServiceEvent):
    type: ClassVar[str] = "joystickdisconnected"

    def __init__(self, inputDevice: InputDevice):
        self.inputDevice = inputDevice


InputServiceEventType = Literal[
    "deviceconnected",
    "devicedisconnected",
    "gamepadconnected",
    "gamepaddisconnected",
]
InputServiceEventListener = Callable[[InputServiceEvent], None]

DeviceConnectedEventListener = Callable[[DeviceConnectedEvent], None]

# T = TypeVar("T", bound=Event)
# T = TypeVar("T", covariant=True)
# T = TypeVar("U", bound=Callable[[T], None])

# class Stack(Generic[T]):


class EventHelpersTypedDict(TypedDict):
    deviceconnected: EventHelper[DeviceConnectedEvent]
    devicedisconnected: EventHelper[DeviceDisconnectedEvent]
    gamepadconnected: EventHelper[GamepadConnectedEvent]
    gamepaddisconnected: EventHelper[GamepadDisconnectedEvent]
    # gamepadconnected: EventHelper[GamepadConnectedEvent]
    # gamepaddisconnected: EventHelper[GamepadDisconnectedEvent]


class GamepadButton:
    def __init__(self, pressed: bool):
        self.pressed = pressed


class Gamepad:
    def __init__(self, inputDevice: InputDeviceWithState):
        self._inputDevice = inputDevice
        self.buttons = [
            GamepadButton(False) for _ in range(inputDevice.numButtons)
        ]

    # @property
    # def buttons(self):
    #     return self._inputDevice.

    def update(self) -> "Gamepad":
        inputDevice = self._inputDevice
        for i in range(inputDevice.numButtons):
            self.buttons[i].pressed = inputDevice.state.buttons[i] != 0
        return self


class InputService:
    def __init__(self) -> None:
        log.info("Creating input service")

        self.eventHelpers: EventHelpersTypedDict = {
            "deviceconnected": EventHelper[DeviceConnectedEvent](
                DeviceConnectedEvent
            ),
            "devicedisconnected": EventHelper[DeviceDisconnectedEvent](
                DeviceDisconnectedEvent
            ),
            "gamepadconnected": EventHelper[GamepadConnectedEvent](
                GamepadConnectedEvent
            ),
            "gamepaddisconnected": EventHelper[GamepadDisconnectedEvent](
                GamepadDisconnectedEvent
            ),
        }

        self.joysticks: List[InputDeviceWithState] = []

        self.gamepads: List[Gamepad] = []
        self.devices: List[InputDeviceWithState] = []

        self.deviceConnectedEvent = EventHelper(DeviceConnectedEvent)
        self.deviceDisconnectedEvent = EventHelper(DeviceDisconnectedEvent)

        self.joystickConnectedEvent = EventHelper(JoystickConnectedEvent)
        self.joystickDisconnectedEvent = EventHelper(JoystickDisconnectedEvent)

        self.gamepadConnectedEvent = EventHelper(GamepadConnectedEvent)
        self.gamepadDisconnectedEvent = EventHelper(GamepadDisconnectedEvent)

        self.deviceHelperThread = DeviceHelperThread(self)
        self.deviceHelperThread.start()

        self.keyboardDevice = InputDeviceWithState(
            InputDeviceType.KEYBOARD,
            "keyboard-instance-0",
            "Keyboard",
            "",
            "",
            0,
            0,
            0,
            0,
        )
        self.devices.append(self.keyboardDevice)

        self.mouseDevice = InputDeviceWithState(
            InputDeviceType.MOUSE,
            "mouse-instance-0",
            "Mouse",
            "",
            "",
            0,
            0,
            0,
            0,
        )
        self.devices.append(self.mouseDevice)

        # FIXME: Listen to Application.quitEvent or Application.exitEvent
        # application = useApplication()
        useMainLoop().exitEvent.addListener(self.onExit)

    def findDeviceByGuid(
        self, deviceGuid: str
    ) -> Optional[InputDeviceWithState]:
        for device in self.devices:
            if device.sdlGuid == deviceGuid:
                return device
        # raise LookupError(deviceGuid)
        return None

    def findDevicesByGuid(self, deviceGuid: str) -> List[InputDeviceWithState]:
        # result: List[InputDeviceWithState] = []
        # for device in self.devices:
        #     if device.sdlGuid == deviceGuid:
        #         result.append(device)
        # raise LookupError(deviceGuid)
        # return None
        return [x for x in self.devices if x.sdlGuid == deviceGuid]

    def getDevices(self) -> List[InputDevice]:
        return [x for x in self.devices]

    def getJoysticks(self) -> List[InputDevice]:
        return [x for x in self.joysticks]

    def getKeyboard(self) -> List[InputDevice]:
        return [self.keyboardDevice]

    def getMice(self) -> List[InputDevice]:
        return [self.mouseDevice]

    # def getGamepads(self) -> List[Gamepad]:
    #     # for gamepad in self.gamepads:
    #     #     gamepad.update()
    #     # return self.gamepads
    #     return [gamepad.update() for gamepad in self.gamepads]

    def onExit(self) -> None:
        log.debug("InputService received exit event")
        self.deviceHelperThread.stop()

    @overload
    def addEventListener(
        self,
        type: Literal["deviceconnected"],
        listener: DeviceConnectedEventListener,
    ) -> SimpleCallable:
        ...

    @overload
    def addEventListener(
        self,
        type: Literal["devicedisconnected"],
        listener: Callable[[DeviceDisconnectedEvent], None],
    ) -> SimpleCallable:
        ...

    @overload
    def addEventListener(
        self,
        type: Literal["gamepadconnected"],
        listener: Callable[[GamepadConnectedEvent], None],
    ) -> SimpleCallable:
        ...

    @overload
    def addEventListener(
        self,
        type: Literal["gamepaddisconnected"],
        listener: Callable[[GamepadDisconnectedEvent], None],
    ) -> SimpleCallable:
        ...

    def addEventListener(
        self,
        type: InputServiceEventType,
        listener: Union[
            Callable[[DeviceConnectedEvent], None],
            Callable[[DeviceDisconnectedEvent], None],
            Callable[[GamepadConnectedEvent], None],
            Callable[[GamepadDisconnectedEvent], None],
        ],
    ) -> SimpleCallable:
        # if type == "deviceconnected":
        #     print(listener)
        #     listener = cast(Callable[[DeviceConnectedEvent], None], listener)
        #     self.deviceConnected.addListener(listener)

        # def removeEventListener() -> None:
        #     self.removeEventListener(type, listener)
        #
        # return removeEventListener

        return self.eventHelpers[type].addListener(listener)  # type: ignore

    def removeEventListener(
        self,
        type: InputServiceEventType,
        listener: Union[
            Callable[[DeviceConnectedEvent], None],
            Callable[[DeviceDisconnectedEvent], None],
            Callable[[GamepadConnectedEvent], None],
            Callable[[GamepadDisconnectedEvent], None],
        ],
    ) -> None:
        self.eventHelpers[type].removeListener(listener)  # type: ignore

    def getJoystickNameByGuid(self, deviceGuid: str) -> str:
        for joystick in self.joysticks:
            if joystick.sdlGuid == deviceGuid:
                return joystick.name
        return ""

    def getGameControllerMapping(
        self, deviceGuid: str
    ) -> Optional[GameControllerMapping]:
        mapping = useGameControllerDB().getMapping(deviceGuid)
        if mapping is not None:
            return mapping.copy()
        return None

    def saveGameControllerMapping(
        # self, mapping: GameControllerMapping, device: Optional[InputDevice] = None
        self,
        mapping: GameControllerMapping,
        device: Optional[InputDevice] = None
    ) -> None:
        log.debug("saveGameControllerMapping mapping=%r", mapping)
        # log.debug("saveGameControllerMapping mapping=%r device=%r", mapping, device)
        # if device is not None:
        #     extra = f"{device.sdlName},axes:{device.numAxes},balls:{device.numBalls},buttons:{device.numButtons},hats:{device.numHats}"
        # else:
        #     extra = ""
        # return useGameControllerDB().saveUserMapping(mapping, extra)
        try:
            LegacyConfig(mapping, device).save()
        except Exception:
            # Legacy config writing is considered a nice to have, so we ignore
            # errors here.
            log.exception("Error writing legacy config")
        return useGameControllerDB().saveUserMapping(mapping)

    def deleteGameControllerMapping(self, deviceGuid: str) -> None:
        return useGameControllerDB().deleteUserMapping(deviceGuid)


from fsgamesys.amiga.fsuaedevicehelper import FSUAEDeviceHelper


class DeviceHelper:
    def __init__(self) -> None:
        self.process: Optional[subprocess.Popen[bytes]] = None

    def start(self) -> None:
        log.info("DeviceHelper starting")
        # self.process = Popen[]
        self.process = FSUAEDeviceHelper.start_with_args(
            ["--events"], stdout=subprocess.PIPE
        )

    def stop(self) -> None:
        log.info("DeviceHelper stopping...")
        # FIXME: Do this in a cleaner way
        # - First send a nice please shut down message?
        # - Then register the process with fscore.exit/cleanup or something
        #   like that (e.g. fscore.exit.cleanupProcess(p))
        # - Also for threads? fscore.exit.cleanupThread(p)
        # Or just register processes and threads when they're created and
        # let the shutdown of the app clean them up with timeout.
        if self.process:
            log.info("Sending kill signal to device helper")
            self.process.kill()
            self.process = None


class JoystickAxisMessage(TypedDict):
    sdlInstanceId: int
    axis: int
    state: int


class JoystickButtonMessage(TypedDict):
    sdlInstanceId: int
    button: int
    state: int


class JoystickHatMessage(TypedDict):
    sdlInstanceId: int
    hat: int
    state: int


class JoystickAddedMessage(TypedDict):
    sdlInstanceId: int
    sdlGuid: str
    sdlName: str
    buttons: int
    axes: int
    hats: int
    balls: int


class JoystickRemovedMessage(TypedDict):
    sdlInstanceId: int


class DeviceHelperThread(threading.Thread):
    # FIXME: Take notification service as a parameter, so that we don't
    # construct the notification service in a thread?
    # or create in the constructor = good enough
    def __init__(self, inputService: InputService) -> None:
        super().__init__()
        self.deviceHelper: Optional[DeviceHelper] = None
        # self.notificationService = useNotificationService()
        self.syncLock = threading.Lock()
        self.lastDebugWasAxis = False

        self.devices: List[InputDeviceWithState] = []
        self.deviceBySdlInstanceId: Dict[int, InputDeviceWithState] = {}
        # self.messages = queue.Queue[str]()

        self.inputService = inputService
        # From Python documentation: Deques support thread-safe, memory
        # efficient appends and pops from either side of the deque. So, no
        # locking should be needed here
        self.messages: Deque[str] = collections.deque()

    def run(self) -> None:
        try:
            log.info("DeviceHelperThread started")
            self.inner()
        except Exception:
            # FIXME: Should probably show user warning here, since input will
            # stop working...
            log.exception("Exception occurred in DeviceHelperThread")
        finally:
            log.info("DeviceHelperThread stopped")
        # Break reference cycle
        del self.inputService

    def inner(self) -> None:
        deviceHelper = DeviceHelper()
        deviceHelper.start()
        self.deviceHelper = deviceHelper
        while True:
            assert deviceHelper.process is not None
            assert deviceHelper.process.stdout is not None
            lineBytes = deviceHelper.process.stdout.readline()
            if len(lineBytes) == 0:
                log.info("No more output from device helper")
                break
            line = lineBytes.decode("UTF-8").strip()
            # log.debug("Got message: %r", line)
            try:
                self.handleLine(line)
            except Exception:
                log.exception(
                    "Exception occurred in DeviceHelperThread.handleLine"
                    "while handling the line %r",
                    line,
                )
                # FIXME: User warning, something like this:
                # fscore.userwarning. - or -
                # useNotificationService
                # notificationService.warn("ERROR_IN_INPUT_HANDLING", ...)

    def stop(self) -> None:
        log.info("DeviceHelperThread got stop message")
        if self.deviceHelper:
            self.deviceHelper.stop()

    def handleLine(self, line: str) -> None:
        self.messages.append(line)
        # FIXME: Send an event after adding a message?
        if line.startswith("#"):
            return
        doc = json.loads(line)
        type = doc["type"]
        # if doc["type"] == "joy-axis-motion" and self.lastDebugWasAxis:
        #     # We do not want to log every axis events; there are too many.
        #     pass
        # else:

        if type == "joy-axis-motion":
            if self.lastDebugWasAxis:
                # We do not want to log every axis events (too many).
                pass
            else:
                log.debug("%r (skipping subsequent axis log messages)", doc)
                self.lastDebugWasAxis = True
        else:
            log.debug("%r", doc)
            self.lastDebugWasAxis = False

        if type == "joy-axis-motion":
            self.handleJoystickAxis(cast(JoystickAxisMessage, doc))
        elif type == "joy-button-up" or type == "joy-button-down":
            self.handleJoystickButton(cast(JoystickButtonMessage, doc))
        elif type == "joy-hat-motion":
            self.handleJoystickHat(cast(JoystickHatMessage, doc))
        elif type == "joy-device-added":
            self.handleJoystickAdded(cast(JoystickAddedMessage, doc))
        elif type == "joy-device-removed":
            self.handleJoystickRemoved(cast(JoystickRemovedMessage, doc))

    def handleJoystickAdded(self, message: JoystickAddedMessage) -> None:
        name = message["sdlName"]
        sdlInstanceId = message["sdlInstanceId"]

        # FIXME: Use name from gamecontrollerdb... !
        # FIXME: Thread synchronizatoin (do in main)
        # FIXME: How to handle when name changed via controller config?
        # FIXME: Maybe a fake disconnect and reconnect with new name?
        # FIXME: Or let clients listen for mapping updated events (incl. name)

        device = InputDeviceWithState(
            InputDeviceType.JOYSTICK,
            name=name,
            instanceId=f"joystick-instance-{sdlInstanceId}",
            sdlName=message["sdlName"],
            sdlGuid=message["sdlGuid"],
            numAxes=message["axes"],
            numBalls=message["balls"],
            numButtons=message["buttons"],
            numHats=message["hats"],
        )
        device.connected = True
        self.devices.append(device)
        self.deviceBySdlInstanceId[sdlInstanceId] = device

        # @runsInMainLoop
        def notifyJoystickAdded() -> None:
            self.inputService.devices.append(device)
            self.inputService.joysticks.append(device)
            self.inputService.deviceConnectedEvent.emit(
                DeviceConnectedEvent(device)
            )
            self.inputService.joystickConnectedEvent.emit(
                JoystickConnectedEvent(device)
            )

            # self.inputService.gamepads.append(Gamepad(device))
            # self.inputService.gamepadConnectedEvent.emit(
            #     GamepadConnectedEvent(device)
            # )

        useMainLoop().run(notifyJoystickAdded)

    def handleJoystickRemoved(self, message: JoystickRemovedMessage) -> None:
        sdlInstanceId = message["sdlInstanceId"]
        for key, value in self.deviceBySdlInstanceId.items():
            if key == sdlInstanceId:
                del self.deviceBySdlInstanceId[key]
                device = value  #  self.devices.remove(value)
                break
        else:
            log.warning(
                "Got joystick removed message, but did not find any entry for "
                "existing device"
            )
            return

        device.connected = False
        self.devices.remove(device)
        print(self.devices)

        def notifyJoystickRemoved() -> None:
            log.debug("notifyJoystickRemoved running in main")
            self.inputService.devices.remove(device)
            self.inputService.joysticks.remove(device)

            self.inputService.joystickDisconnectedEvent.emit(
                JoystickDisconnectedEvent(device)
            )
            self.inputService.deviceDisconnectedEvent.emit(
                DeviceDisconnectedEvent(device)
            )

            # self.inputService.gamepads.remove(device)
            # self.inputService.gamepadDisconnectedEvent.emit(
            #     GamepadDisconnectedEvent(device)
            # )

        useMainLoop().run(notifyJoystickRemoved)

    def handleJoystickAxis(self, message: JoystickAxisMessage) -> None:
        sdlInstanceId = message["sdlInstanceId"]
        device = self.deviceBySdlInstanceId[sdlInstanceId]
        state = int(message["state"])
        device.state.axes[message["axis"]] = max(
            -1.0, min(1.0, state / 32768 if state < 0 else state / 32767)
        )

    def handleJoystickButton(self, message: JoystickButtonMessage) -> None:
        sdlInstanceId = message["sdlInstanceId"]
        device = self.deviceBySdlInstanceId[sdlInstanceId]
        device.state.buttons[message["button"]] = message["state"]

    def handleJoystickHat(self, message: JoystickHatMessage) -> None:
        sdlInstanceId = message["sdlInstanceId"]
        device = self.deviceBySdlInstanceId[sdlInstanceId]
        device.state.hats[message["hat"]] = HatState(message["state"])


_instance: Optional[InputService] = None


def useInputService() -> InputService:
    global _instance
    if _instance is None:
        _instance = InputService()
    return _instance
