from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from fsgs.mednafen.mednafen import MednafenRunner


class LynxRunner(MednafenRunner):

    CONTROLLER = {
        "type": "gamepad",
        "description": "Built-in Controller",
        "mapping_name": "gamegear",
    }

    PORTS = [
        {
            "description": "Controller",
            "types": [CONTROLLER]
        },
    ]

    def __init__(self, fsgs):
        super().__init__(fsgs)

    def mednafen_system_prefix(self):
        return "lynx"

    def mednafen_input_mapping(self, _):
        return {
            "A": "lynx.input.builtin.gamepad.a",
            "B": "lynx.input.builtin.gamepad.b",
            "UP": "lynx.input.builtin.gamepad.up",
            "DOWN": "lynx.input.builtin.gamepad.down",
            "LEFT": "lynx.input.builtin.gamepad.left",
            "RIGHT": "lynx.input.builtin.gamepad.right",
            "OPTION1": "lynx.input.builtin.gamepad.option_1",
            "OPTION2": "lynx.input.builtin.gamepad.option_2",
            "PAUSE": "lynx.input.builtin.gamepad.pause",
        }
