from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals


import json
from fsgs.mame.mame import MAMERunner


class ArcadeRunner(MAMERunner):

    CONTROLLER = {
        "type": "controller",
        "description": "Controller",
        "mapping_name": "arcade",
    }

    PORTS = [
        {
            "description": "1st Controller",
            "types": [CONTROLLER]
        }, {
            "description": "2nd Controller",
            "types": [CONTROLLER]
        }, {
            "description": "3rd Controller",
            "types": [CONTROLLER]
        }, {
            "description": "4th Controller",
            "types": [CONTROLLER]
        },
    ]

    def mame_romset(self):
        name = self.config["mame_rom_set"]
        files = {}
        for entry in json.loads(self.config["file_list"]):
            files[entry["sha1"]] = entry["name"]
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
            "button_order", "1 2 3 4 5 6 7 8 9 10 11 12")
        b = 0
        for button in button_order.split(" "):
            button = button.strip()
            if button:
                b += 1
                mapping[str(b)] = "P#_BUTTON" + button
        return mapping
