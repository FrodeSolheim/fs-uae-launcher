import logging
import os
from typing import Dict, List, Optional

from fscore.system import System
from fsgamesys.FSGSDirectories import FSGSDirectories
from fsgamesys.input.gamecontroller import (
    GameControllerItem,
    GameControllerMapping,
)
from fsgamesys.input.inputdevice import InputDevice

log = logging.getLogger(__name__)


class LegacyConfig:
    """Write controller configs compatible with FS-UAE 3."""

    def __init__(
        self,
        mapping: GameControllerMapping,
        device: Optional[InputDevice] = None,
    ):
        self.mapping = mapping
        self.device = device
        self.device_name = self.mapping.name
        if System.linux:
            self.platform = "linux"
        elif System.windows:
            self.platform = "windows"
        elif System.macos:
            self.platform = "macos"

    @staticmethod
    def get_save_path(file_name: str) -> str:
        dest = FSGSDirectories.get_controllers_dir()
        if not os.path.exists(dest):
            os.makedirs(dest)
        dest = os.path.join(dest, file_name)
        return dest

    def get_joystick_id(self) -> str:
        platform = self.platform
        if self.device is None:
            raise Exception("Cannot create joystick ID")
        device_name = self.device.sdlName.rsplit("#", 1)[0]
        buttons = self.device.numButtons
        axes = self.device.numAxes
        hats = self.device.numHats
        balls = self.device.numBalls
        name_lower = device_name.lower()
        name = ""
        for c in name_lower:
            if c in "abcdefghijklmnopqrstuvwxyz0123456789":
                name = name + c
            else:
                if not name.endswith("_"):
                    name += "_"
        name = name.strip("_")
        return "{0}_{1}_{2}_{3}_{4}_{5}".format(
            name, buttons, axes, hats, balls, platform
        )

    def _getConfigLines(self) -> List[str]:
        platform = self.platform
        device_name = self.device_name.rsplit("#", 1)[0]
        config = [
            "[fs-uae-controller]",
            "name = {}".format(device_name),
            "platform = {}".format(platform),
            "",
        ]
        # config.extend(
        #     [
        #         "[device]",
        #         "make = {}".format(device_make),
        #         "model = {}".format(device_model),
        #         "type = {}".format(device_type),
        #         "",
        #     ]
        # )
        if self.device is not None:
            config.extend(
                [
                    "[sdl]",
                    "guid = {}".format(self.device.sdlGuid),
                    "buttons = {}".format(self.device.numButtons),
                    "hats = {}".format(self.device.numHats),
                    "axes = {}".format(self.device.numAxes),
                    "balls = {}".format(self.device.numBalls),
                    "",
                ]
            )

        config.extend(
            [
                "[default]",
                "include = universal_gamepad",
            ]
        )
        button_config: List[str] = []
        for key, value in self.getLegacyMapping().items():
            button_config.append("{0} = {1}".format(key, value))
        config.extend(sorted(button_config))
        return config

    def _writeConfigToFile(self, fileName: str, config: List[str]):
        with open(fileName, "w", encoding="UTF-8") as f:
            for line in config:
                f.write(line)
                f.write("\n")

    def save(self) -> None:
        guid = self.mapping.guid
        config = self._getConfigLines()
        try:
            joystick_id = self.get_joystick_id()
        except Exception:
            log.exception("Could not get joystick ID")
        else:
            self._writeConfigToFile(self.get_save_path(joystick_id + ".conf"), config)
        if len(guid) == 32:
            self._writeConfigToFile(self.get_save_path(guid + ".fs-uae-controller"), config)

    def saveToFile(self, fileName: str):
        config = self._getConfigLines()
        self._writeConfigToFile(fileName, config)

    def getLegacyMapping(self) -> Dict[str, str]:
        legacyMapping: Dict[str, str] = {}
        for item, bind in self.mapping.binds.items():
            legacyItem = itemToLegacyMapping[item]
            legacyBind = bind.toLegacyConfig()
            if item == GameControllerItem.LEFTX:
                legacyMapping[f"{legacyBind}_neg"] = "lstick_left"
                legacyMapping[f"{legacyBind}_pos"] = "lstick_right"
            elif item == GameControllerItem.LEFTY:
                legacyMapping[f"{legacyBind}_neg"] = "lstick_up"
                legacyMapping[f"{legacyBind}_pos"] = "lstick_down"
            elif item == GameControllerItem.RIGHTX:
                legacyMapping[f"{legacyBind}_neg"] = "rstick_left"
                legacyMapping[f"{legacyBind}_pos"] = "rstick_right"
            elif item == GameControllerItem.RIGHTY:
                legacyMapping[f"{legacyBind}_neg"] = "rstick_up"
                legacyMapping[f"{legacyBind}_pos"] = "rstick_down"
            else:
                if (
                    legacyBind.startswith("axis_")
                    and not legacyBind.endswith("_neg")
                    and not legacyBind.endswith("_pos")
                ):
                    # Legacy configs does not understand whole axes
                    legacyBind = f"{legacyBind}_pos"
                legacyMapping[legacyBind] = legacyItem
        return legacyMapping


itemToLegacyMapping = {
    GameControllerItem.A: "south_button",
    GameControllerItem.B: "east_button",
    GameControllerItem.X: "west_button",
    GameControllerItem.Y: "north_button",
    GameControllerItem.BACK: "select_button",
    GameControllerItem.GUIDE: "menu_button",
    GameControllerItem.START: "start_button",
    GameControllerItem.LEFTSTICK: "lstick_button",
    GameControllerItem.RIGHTSTICK: "rstick_button",
    GameControllerItem.LEFTSHOULDER: "left_shoulder",
    GameControllerItem.RIGHTSHOULDER: "right_shoulder",
    GameControllerItem.DPAD_UP: "dpad_up",
    GameControllerItem.DPAD_DOWN: "dpad_down",
    GameControllerItem.DPAD_LEFT: "dpad_left",
    GameControllerItem.DPAD_RIGHT: "dpad_right",
    GameControllerItem.LEFTX: "",
    GameControllerItem.LEFTY: "",
    GameControllerItem.RIGHTX: "",
    GameControllerItem.RIGHTY: "",
    GameControllerItem.TRIGGERLEFT: "left_trigger",
    GameControllerItem.TRIGGERRIGHT: "right_trigger",
}
