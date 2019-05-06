from fsgs.drivers.mednafendriver import MednafenDriver

"""

FIXME: Some PAL games are 256x240, e.g. Fantastic Dizzy
"""


class MednafenSMSDriver(MednafenDriver):
    CONTROLLER = {
        "type": "gamepad",
        "description": "Gamepad",
        "mapping_name": "mastersystem",
    }

    PORTS = [
        {"description": "1st Controller", "types": [CONTROLLER]},
        {"description": "2nd Controller", "types": [CONTROLLER]},
    ]

    def __init__(self, fsgs):
        super().__init__(fsgs)

    def mednafen_system_prefix(self):
        return "sms"

    def mednafen_input_mapping(self, port):
        if port == 0:
            return {
                "1": "sms.input.port1.gamepad.fire1",
                "2": "sms.input.port1.gamepad.fire2",
                "UP": "sms.input.port1.gamepad.up",
                "DOWN": "sms.input.port1.gamepad.down",
                "LEFT": "sms.input.port1.gamepad.left",
                "RIGHT": "sms.input.port1.gamepad.right",
                "PAUSE": "sms.input.port1.gamepad.pause",
            }
        elif port == 1:
            return {
                "1": "sms.input.port2.gamepad.fire1",
                "2": "sms.input.port2.gamepad.fire2",
                "UP": "sms.input.port2.gamepad.up",
                "DOWN": "sms.input.port2.gamepad.down",
                "LEFT": "sms.input.port2.gamepad.left",
                "RIGHT": "sms.input.port2.gamepad.right",
                "PAUSE": "sms.input.port2.gamepad.pause",
            }

        # FIXME: add PAUSE button to universal gamepad config

    def game_video_par(self):
        size = self.game_video_size()
        return (4 / 3) / (size[0] / size[1])

    def game_video_size(self):
        if self.is_pal():
            size = (256, 240)
        else:
            size = (256, 192)
        return size
