from fsgamesys import Option
from fsgamesys.drivers.mednafendriver import MednafenDriver
from fsgamesys.knownfiles import KnownFile
from fsgamesys.platforms.loader import SimpleLoader
from fsgamesys.platforms.platform import Platform

PSX_PLATFORM_ID = "PSX"
PSX_PLATFORM_NAME = "PlayStation"
# noinspection SpellCheckingInspection
PSX_SCPH5500_BIN_SHA1 = "b05def971d8ec59f346f2d9ac21fb742e3eb6917"
# noinspection SpellCheckingInspection
PSX_SCPH5501_BIN_SHA1 = "0555c6fae8906f3f09baf5988f00e55f88e9f30b"
# noinspection SpellCheckingInspection
PSX_SCPH5502_BIN_SHA1 = "f6bc2d1f5eb6593de7d089c425ac681d6fffd3f0"
PSX_GAMEPAD = {
    "type": "gamepad",
    "description": "Digital Gamepad",
    "mapping_name": "playstation",
}
PSX_DUALSHOCK = {
    "type": "dualshock",
    "description": "DualShock Gamepad",
    "mapping_name": "playstation",  # FIXME
}
PSX_MOUSE = {
    "type": "mouse",
    "description": "PlayStation Mouse",
    "mapping_name": "",  # FIXME
}
PSX_SCPH5500_BIN = KnownFile(
    "b05def971d8ec59f346f2d9ac21fb742e3eb6917", PSX_PLATFORM_ID, "scph5500.bin"
)
PSX_SCPH5501_BIN = KnownFile(
    "0555c6fae8906f3f09baf5988f00e55f88e9f30b", PSX_PLATFORM_ID, "scph5501.bin"
)
# noinspection SpellCheckingInspection
PSX_SCPH5502_BIN = KnownFile(
    "f6bc2d1f5eb6593de7d089c425ac681d6fffd3f0", PSX_PLATFORM_ID, "scph5502.bin"
)
PSX_ROMS_FOR_REGION = {
    "JA": ["scph5500.bin", PSX_SCPH5500_BIN.sha1],
    "US": ["scph5501.bin", PSX_SCPH5501_BIN.sha1],
    "EU": ["scph5502.bin", PSX_SCPH5502_BIN.sha1],
}
PSX_MODEL_NTSC = "ntsc"
PSX_MODEL_NTSC_J = "ntsc-j"
PSX_MODEL_PAL = "pal"


class PlayStationPlatform(Platform):
    # FIXME: Move to init instead
    PLATFORM_NAME = PSX_PLATFORM_NAME

    def driver(self, fsgc):
        return PlayStationMednafenDriver(fsgc)

    def loader(self, fsgc):
        return PlayStationLoader(fsgc)


class PlayStationLoader(SimpleLoader):
    def load_files(self, values):
        self.config["cue_sheets"] = values["cue_sheets"]
        self.config["file_list"] = values["file_list"]
        self.config["sbi_data"] = values["sbi_data"]

    def load_extra(self, values):
        self.config[Option.PSX_MODEL] = values["psx_model"]
        self.config[Option.PSX_PORT_1_TYPE] = values["psx_port_1_type"]
        self.config[Option.PSX_PORT_2_TYPE] = values["psx_port_2_type"]


PSX_PORTS = [
    {
        "description": "Port 1",
        "types": [PSX_GAMEPAD, PSX_DUALSHOCK, PSX_MOUSE],
        "type_option": "psx_port_1_type",
        "device_option": "psx_port_1",
    },
    {
        "description": "Port 2",
        "types": [PSX_GAMEPAD, PSX_DUALSHOCK, PSX_MOUSE],
        "type_option": "psx_port_2_type",
        "device_option": "psx_port_2",
    },
]


class PlayStationMednafenDriver(MednafenDriver):
    PORTS = PSX_PORTS

    def __init__(self, fsgc):
        super().__init__(fsgc)
        self.helper = PlayStationHelper(self.options)

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

        pfx = self.mednafen_system_prefix()

        self.emulator.args.extend(
            ["-{}.input.port1".format(pfx), self.ports[0].type]
        )
        self.emulator.args.extend(
            ["-{}.input.port2".format(pfx), self.ports[1].type]
        )

        # self.init_mednafen_crop_from_viewport()
        self.set_mednafen_aspect(4, 3)
        # We do aspect calculation separately. Must not be done twice.
        # self.emulator.args.extend(["-psx.correct_aspect", "0"])

        self.emulator.args.extend(["-psx.region_autodetect", "0"])
        if self.helper.model() == PSX_MODEL_PAL:
            self.prepare_mednafen_bios(PSX_SCPH5502_BIN, "scph5502.bin")
            self.emulator.args.extend(["-psx.region_default", "eu"])
        elif self.helper.model() == PSX_MODEL_NTSC_J:
            self.prepare_mednafen_bios(PSX_SCPH5500_BIN, "scph5500.bin")
            self.emulator.args.extend(["-psx.region_default", "jp"])
        else:
            self.prepare_mednafen_bios(PSX_SCPH5501_BIN, "scph5501.bin")
            self.emulator.args.extend(["-psx.region_default", "na"])

        if self.options[Option.PSX_PRELOAD] == "1":
            self.emulator.args.extend(["-cd.image_memcache", "1"])

        self.prepare_mednafen_cd_images()

    def get_game_file(self, config_key="cartridge_slot"):
        return None


class PlayStationHelper:
    def __init__(self, options):
        self.options = options

    def model(self):
        model = self.options[Option.PSX_MODEL]
        if model in ["", PSX_MODEL_NTSC]:
            return PSX_MODEL_NTSC
        elif model == PSX_MODEL_PAL:
            return PSX_MODEL_PAL
        elif model == PSX_MODEL_NTSC_J:
            return PSX_MODEL_NTSC_J
        else:
            print("[PSX] Warning: Invalid model:", model)
            return PSX_MODEL_NTSC

    def pal(self):
        return self.model() == PSX_MODEL_PAL
