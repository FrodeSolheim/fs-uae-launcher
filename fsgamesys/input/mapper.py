from logging import getLogger
from typing import Dict, Iterator, List, Optional, Tuple

from fscore.system import System
from fsgamesys.drivers.gamedriver import Port
from fsgamesys.input.inputdevice import InputDevice, InputDeviceType
from fsgamesys.input.inputservice import useInputService
from fsgamesys.input.keyboard import Keyboard
from fsgamesys.input.legacyinputdevice import (
    LegacyInputDevice as LegacyInputDevice,
)
from fsgamesys.input.legacyconfig import LegacyConfig


log = getLogger(__name__)


# def itemToLegacy(item: GameControllerItem):
#     return


def configureController(
    device: InputDevice, mappingName: str, multiple: bool
) -> Dict[str, str]:
    legacyDevice = LegacyInputDevice("", "", [], version=2)

    config: Dict[str, str] = {}
    legacyDevice.read_config(
        "universal_gamepad", config, mappingName, multiple
    )

    inputService = useInputService()
    controllerMapping = inputService.getGameControllerMapping(device.sdlGuid)
    if controllerMapping is None:
        # FIXME: UserWarningException or something instead
        # FIXME: MessageException?
        # FIXME: Maybe check for this earlier in the process also.
        raise Exception(
            f'Controller "{device.name}" is not configured. '
            "Please do this via Preferences -> Controllers and try again."
        )
    # legacyConfig: List[Tuple[str, str]] = []
    legacyMapping = LegacyConfig(controllerMapping).getLegacyMapping()
    # legacyConfig: Dict[str, str] = {}
    # for item, bind in controllerMapping.binds.items():
    #     legacyItem = itemToLegacyMapping[item]

    #     print("FIXME: SUPPORT FOR MAPPING LEFTX, LEFTY, RIGHTX, RIGHTY")

    #     legacyConfig[bind.toLegacyConfig()] = legacyItem

    print("")
    print(config)
    # legacyDevice.read_config_2(config, list(legacyConfig.items()), multiple)
    legacyDevice.read_config_2(config, legacyMapping.items(), multiple)
    print("")
    print("")
    print(config)
    print("")

    # FIXME: Idea: In game drivers, warn if not all platform controller actions
    # could be mapped to the currently chosen device (e.g. missing some buttons)

    return config


def configureKeyboard(
    device: InputDevice, mappingName: str, multiple: bool
) -> Dict[str, str]:
    legacyDevice = LegacyInputDevice(mappingName, "Keyboard", [], version=2)
    return legacyDevice.get_config()


def configureDevice(
    device: InputDevice, mappingName: str, multiple: bool
) -> Dict[str, str]:
    log.debug("configureDevice %r for %r", device, mappingName)
    if device.type == InputDeviceType.KEYBOARD:
        config = configureKeyboard(device, mappingName, multiple)
    elif device.type == InputDeviceType.JOYSTICK:
        config = configureController(device, mappingName, multiple)
    else:
        config = {}
    print("")
    print(config)
    print("")
    return config


class InputMapper(object):
    def __init__(
        self, port: Port, mapping: Dict[str, str], multiple: bool = True
    ):
        self.port = port
        self.device: Optional[InputDevice] = port.device
        self.mapping = mapping
        self.multiple = multiple
        print(
            "[INPUT] Port",
            port.number,
            "Device:",
            self.device.id if self.device is not None else "(none)",
        )
        print("[INPUT] Port", port.number, "mapping:", mapping)

    def items(self) -> Iterator[Tuple[str, str]]:
        # input = self.input
        # if not input.device_config:
        #     return
        if not self.device:
            return

        # config = self.device.configure(
        #     self.port.mapping_name, multiple=self.multiple
        # )
        config = configureDevice(
            self.device, self.port.mapping_name, multiple=self.multiple
        )

        # print(config)
        print("mapping:", self.mapping)
        for native_button, game_button in config.items():
            game_button = game_button.upper()
            print("******", native_button, game_button)
            try:
                input_key = self.mapping[game_button]
            except KeyError:
                pass
            else:
                print("input_key", input_key)
                input_value = self.calc_input(native_button)
                # print("---->", input_key, input_value)
                # f.write('{input_key} = "{input_value}"\n'.format(
                #         input_key=input_key,
                #         input_value=input_value))
                if input_value is not None:
                    yield input_key, input_value

    def axis(self, axis: int, positive: bool) -> str:
        raise NotImplementedError()

    def hat(self, hat: int, direction: int) -> str:
        raise NotImplementedError()

    def button(self, button: int) -> str:
        raise NotImplementedError()

    def key(self, key: int) -> str:
        raise NotImplementedError()

    def mouse(self, button: int, axis: int, positive: bool):
        # raise NotImplementedError()
        return None

    def calc_input(self, value: str) -> str:
        parts = value.lower().split("_")
        if parts[0] == "axis":
            axis = int(parts[1])
            positive = parts[2] == "pos"
            return self.axis(axis, positive)
        elif parts[0] == "hat":
            hat = int(parts[1])
            direction = parts[2]
            return self.hat(hat, direction)
        elif parts[0] == "button":
            button = int(parts[1])
            return self.button(button)
        elif parts[0] == "key":
            key_name = value.split("_", 1)[1].lower()
            if key_name == "rctrl" and System.macos:
                print("using ralt instead of rctrl on Mac")
                key_name = "ralt"
            key = Keyboard.key(key_name)
            return self.key(key)
        elif parts[0] == "mouse":
            button = 0
            axis = 0
            positive = False
            if parts[1] == "left":
                button = 1
            elif parts[1] == "right":
                button = 2
            elif parts[1] == "middle":
                button = 3
            else:
                axis = int(parts[1])
                positive = parts[2] == "pos"
            return self.mouse(button, axis, positive)
        return None
