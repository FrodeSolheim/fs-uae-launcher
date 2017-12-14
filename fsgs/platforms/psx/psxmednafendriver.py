from fsgs.drivers.mednafendriver import MednafenDriver
from fsgs.platforms.psx.psxplatform import PSX_CONTROLLER
from fsgs.platforms.psx.psxplatform import PSX_SCPH5501_BIN


class PlayStationMednafenDriver(MednafenDriver):
    PORTS = [
        {
            "description": "Input Port 1",
            "types": [PSX_CONTROLLER]
        }, {
            "description": "Input Port 2",
            "types": [PSX_CONTROLLER]
        },
    ]

    def __init__(self, fsgs):
        super().__init__(fsgs)

    def mednafen_input_mapping(self, port):
        if port == 0:
            return {
                "CIRCLE": "psx.input.port1.gamepad.circle",
                "CROSS": "psx.input.port1.gamepad.cross",
                "TRIANGLE": "psx.input.port1.gamepad.triangle",
                "SQUARE": "psx.input.port1.gamepad.square",
                "L1": "psx.input.port1.gamepad.l1",
                "L2": "psx.input.port1.gamepad.l2",
                "R1": "psx.input.port1.gamepad.r1",
                "R2": "psx.input.port1.gamepad.r2",
                "UP": "psx.input.port1.gamepad.up",
                "DOWN": "psx.input.port1.gamepad.down",
                "LEFT": "psx.input.port1.gamepad.left",
                "RIGHT": "psx.input.port1.gamepad.right",
                "SELECT": "psx.input.port1.gamepad.select",
                "START": "psx.input.port1.gamepad.start",
            }
        elif port == 1:
            return {
                "CIRCLE": "psx.input.port2.gamepad.circle",
                "CROSS": "psx.input.port2.gamepad.cross",
                "TRIANGLE": "psx.input.port2.gamepad.triangle",
                "SQUARE": "psx.input.port2.gamepad.square",
                "L1": "psx.input.port2.gamepad.l1",
                "L2": "psx.input.port2.gamepad.l2",
                "R1": "psx.input.port2.gamepad.r1",
                "R2": "psx.input.port2.gamepad.r2",
                "UP": "psx.input.port2.gamepad.up",
                "DOWN": "psx.input.port2.gamepad.down",
                "LEFT": "psx.input.port2.gamepad.left",
                "RIGHT": "psx.input.port2.gamepad.right",
                "SELECT": "psx.input.port2.gamepad.select",
                "START": "psx.input.port2.gamepad.start",
            }

    def mednafen_system_prefix(self):
        return "psx"

    def game_video_size(self):
        # FIXME
        if self.is_pal():
            size = (320, 240)
        else:
            size = (320, 224)
        return size

    def prepare(self):
        super().prepare()

        # self.init_mednafen_crop_from_viewport()
        self.set_mednafen_aspect(4, 3)
        # We do aspect calculation separately. Must not be done twice.
        # self.emulator.args.extend(["-psx.correct_aspect", "0"])

        self.prepare_mednafen_bios(PSX_SCPH5501_BIN, "scph5501.bin")
        self.prepare_mednafen_cd_images()

    def get_game_file(self, config_key="cartridge_slot"):
        return None
