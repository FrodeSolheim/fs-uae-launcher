from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from fsgs.mednafen.mednafen import MednafenRunner


class MegaDriveRunner(MednafenRunner):

    CONTROLLER = {
        "type": "gamepad",
        "description": "Gamepad",
        "mapping_name": "megadrive",
    }

    PORTS = [
        {
            "description": "1st Controller",
            "types": [CONTROLLER]
        }, {
            "description": "2nd Controller",
            "types": [CONTROLLER]
        },
    ]

    def __init__(self, fsgs):
        super().__init__(fsgs)

    def mednafen_system_prefix(self):
        return "md"

    def mednafen_input_mapping(self, port):
        if port == 0:
            return {
                "A": "md.input.port1.gamepad.a",
                "B": "md.input.port1.gamepad.b",
                "C": "md.input.port1.gamepad.c",
                "X": "md.input.port1.gamepad.x",
                "Y": "md.input.port1.gamepad.y",
                "Z": "md.input.port1.gamepad.z",
                "UP": "md.input.port1.gamepad.up",
                "DOWN": "md.input.port1.gamepad.down",
                "LEFT": "md.input.port1.gamepad.left",
                "RIGHT": "md.input.port1.gamepad.right",
                "MODE": "md.input.port1.gamepad.mode",
                "START": "md.input.port1.gamepad.start",
            }
        elif port == 1:
            return {
                "A": "md.input.port2.gamepad.a",
                "B": "md.input.port2.gamepad.b",
                "C": "md.input.port2.gamepad.c",
                "X": "md.input.port2.gamepad.x",
                "Y": "md.input.port2.gamepad.y",
                "Z": "md.input.port2.gamepad.z",
                "UP": "md.input.port2.gamepad.up",
                "DOWN": "md.input.port2.gamepad.down",
                "LEFT": "md.input.port2.gamepad.left",
                "RIGHT": "md.input.port2.gamepad.right",
                "MODE": "md.input.port2.gamepad.mode",
                "START": "md.input.port2.gamepad.start",
            }

        # FIXME: add PAUSE button to universal gamepad config

    #def mednafen_video_size(self):
    #    return 256, 192
