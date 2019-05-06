import json

from fsgs import Option
from fsgs.drivers.mamedriver import MameDriver


class MameArcadeDriver(MameDriver):
    CONTROLLER = {
        "type": "controller",
        "description": "Controller",
        "mapping_name": "arcade",
    }

    PORTS = [
        {"description": "Player 1", "types": [CONTROLLER]},
        {"description": "Player 2", "types": [CONTROLLER]},
        {"description": "Player 3", "types": [CONTROLLER]},
        {"description": "Player 4", "types": [CONTROLLER]},
    ]

    def mame_romset(self):
        name = self.options["mame_rom_set"]
        files = {}
        for entry in json.loads(self.options["file_list"]):
            files[entry["name"]] = entry["sha1"]
        return name, files

    def mame_input_mapping(self, _):
        mapping = {
            "START": "START#",
            "SELECT": "COIN#",
            "UP": "P#_JOYSTICK_UP",
            "DOWN": "P#_JOYSTICK_DOWN",
            "LEFT": "P#_JOYSTICK_LEFT",
            "RIGHT": "P#_JOYSTICK_RIGHT",
        }
        button_order = self.config.get(
            "button_order", "1 2 3 4 5 6 7 8 9 10 11 12"
        )
        b = 0
        for button in button_order.split(" "):
            button = button.strip()
            if button:
                b += 1
                mapping[str(b)] = "P#_BUTTON" + button
        return mapping

    def prepare(self):
        super().prepare()
        if self.options[Option.MAME_ARTWORK] == "1":
            pass
        else:
            self.create_mame_layout()
