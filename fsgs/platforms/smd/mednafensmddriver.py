from fsgs.drivers.mednafendriver import MednafenDriver
from fsgs.option import Option

SMD_MODEL_NTSC_U = "ntsc-u"
SMD_MODEL_NTSC_J = "ntsc-j"
SMD_MODEL_PAL = "pal"
SMD_MODEL_AUTO = "auto"


class MednafenSmdDriver(MednafenDriver):
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
        self.helper = MegaDriveHelper(self.options)

    def prepare(self):
        if self.helper.model() == SMD_MODEL_NTSC_U:
            region = "overseas_ntsc"
        elif self.helper.model() == SMD_MODEL_PAL:
            region = "overseas_pal"
        elif self.helper.model() == SMD_MODEL_NTSC_J:
            region = "domestic_ntsc"
        else:
            region = "game"
        self.emulator.args.extend(["-md.region", region])
        # We do aspect calculation separately. Must not be done twice.
        self.emulator.args.extend(["-md.correct_aspect", "0"])
        # The arguments must be added before the cartridge, which is why
        # we call super().prepare() at the end here.
        super().prepare()

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

    def game_video_par(self):
        # These may not be entirely correct...
        if self.is_pal():
            return (4 / 3) / (320 / 240)
        else:
            return (4 / 3) / (320 / 224)

    def game_video_size(self):
        # FIXME: is_pal should probably be influenced by model now.
        if self.is_pal():
            size = (320, 240)
        else:
            size = (320, 224)
        return size


class MegaDriveHelper:
    def __init__(self, options):
        self.options = options

    def model(self):
        if self.options[Option.SMD_MODEL] == "ntsc-u":
            return SMD_MODEL_NTSC_U
        if self.options[Option.SMD_MODEL] == "ntsc-j":
            return SMD_MODEL_NTSC_J
        if self.options[Option.SMD_MODEL] == "pal":
            return SMD_MODEL_PAL
        return SMD_MODEL_AUTO
