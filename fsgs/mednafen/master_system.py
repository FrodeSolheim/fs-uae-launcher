from fsgs.mednafen.mednafen import MednafenRunner


class MasterSystemRunner(MednafenRunner):

    CONTROLLER = {
        "type": "gamepad",
        "description": "Gamepad",
        "mapping_name": "mastersystem",
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

    # def mednafen_video_size(self):
    #     return 256, 192
