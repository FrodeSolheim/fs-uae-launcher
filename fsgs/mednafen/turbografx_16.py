from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from fsgs.mednafen.mednafen import MednafenRunner


class TurboGrafx16Runner(MednafenRunner):

    CONTROLLER = {
        "type": "gamepad",
        "description": "Gamepad",
        "mapping_name": "turbografx16",
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

    def mednafen_input_mapping(self, port):
        if port == 0:
            return {
                "1": "pce.input.port1.gamepad.i",
                "2": "pce.input.port1.gamepad.ii",
                "UP": "pce.input.port1.gamepad.up",
                "DOWN": "pce.input.port1.gamepad.down",
                "LEFT": "pce.input.port1.gamepad.left",
                "RIGHT": "pce.input.port1.gamepad.right",
                "SELECT": "pce.input.port1.gamepad.select",
                "RUN": "pce.input.port1.gamepad.run",
            }
        elif port == 1:
            return {
                "1": "pce.input.port2.gamepad.i",
                "2": "pce.input.port2.gamepad.ii",
                "UP": "pce.input.port2.gamepad.up",
                "DOWN": "pce.input.port2.gamepad.down",
                "LEFT": "pce.input.port2.gamepad.left",
                "RIGHT": "pce.input.port2.gamepad.right",
                "SELECT": "pce.input.port2.gamepad.select",
                "RUN": "pce.input.port2.gamepad.run",
            }

    def mednafen_system_prefix(self):
        return "pce"

    #def medmafen_video_size(self):
    #    # FIXME
    #    return 256, 240
