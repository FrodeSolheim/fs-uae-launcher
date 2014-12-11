from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from fsgs.mednafen.mednafen import MednafenRunner


class GameBoyColorRunner(MednafenRunner):

    CONTROLLER = {
        "type": "gamepad",
        "description": "Built-in Controller",
        "mapping_name": "gameboycolor",
    }

    PORTS = [
        {
            "description": "Controller",
            "types": [CONTROLLER]
        },
    ]

    def __init__(self, fsgs):
        super().__init__(fsgs)

    def get_game_refresh_rate(self):
        return 59.73

    def mednafen_input_mapping(self, _):
        return {
            "A": "gb.input.builtin.gamepad.a",
            "B": "gb.input.builtin.gamepad.b",
            "UP": "gb.input.builtin.gamepad.up",
            "DOWN": "gb.input.builtin.gamepad.down",
            "LEFT": "gb.input.builtin.gamepad.left",
            "RIGHT": "gb.input.builtin.gamepad.right",
            "SELECT": "gb.input.builtin.gamepad.select",
            "START": "gb.input.builtin.gamepad.start",
        }

    def mednafen_rom_extensions(self):
        return [".gbc"]

    def mednafen_scanlines_setting(self):
        return 33

    def mednafen_special_filter(self):
        return "nn2x"

    def mednafen_system_prefix(self):
        return "gb"

    #def mednafen_video_size(self):
    #    return 160, 144
