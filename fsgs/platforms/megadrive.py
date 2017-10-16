from fsbc import settings
from fsgs.drivers.mednafendriver import MednafenDriver
from fsgs.drivers.mess.messsmddriver import MessSmdDriver
from fsgs.option import Option
from fsgs.platform import Platform
from fsgs.platforms.loader import SimpleLoader

SMD_MODEL_NTSC_U = "ntsc"
SMD_MODEL_NTSC_J = "ntsc-j"
SMD_MODEL_PAL = "pal"
# FIXME: REMOVE MODEL AUTO? It makes it difficult to predict video size
# without inspecting ROM file.
SMD_MODEL_AUTO = "auto"
SMD_CONTROLLER = {
    "type": "gamepad",
    "description": "Gamepad",
    "mapping_name": "megadrive",
}
SMD_PORTS = [
    {
        "description": "Port 1",
        "types": [SMD_CONTROLLER]
    }, {
        "description": "Port 2",
        "types": [SMD_CONTROLLER]
    },
]


class MegaDrivePlatform(Platform):
    PLATFORM_NAME = "Mega Drive"

    def driver(self, fsgc):
        if settings.get(Option.SMD_DRIVER) == "mess":
            return MessSmdDriver(fsgc)
        else:
            return MegaDriveMednafenDriver(fsgc)

    def loader(self, fsgc):
        return MegaDriveLoader(fsgc)


class MegaDriveLoader(SimpleLoader):
    def load_extra(self, values):
        self.config[Option.SMD_MODEL] = values["smd_model"]
        # self.config[Option.SMD_PORT_1_TYPE] = values["smd_port_1_type"]
        # self.config[Option.SMD_PORT_2_TYPE] = values["smd_port_2_type"]
        # self.config[Option.SMD_PORT_3_TYPE] = values["smd_port_3_type"]
        # self.config[Option.SMD_PORT_4_TYPE] = values["smd_port_4_type"]

        # FIXME: Remove later when database contains smd_model
        if not self.config[Option.SMD_MODEL]:
            variant = values["variant_name"].lower()
            if "world" in variant or "usa" in variant:
                model = SMD_MODEL_NTSC_U
            elif "europe" in variant or "australia" in variant:
                model = SMD_MODEL_PAL
            elif "japan" in variant:
                model = SMD_MODEL_NTSC_J
            else:
                # FIXME: Remove?
                model = SMD_MODEL_AUTO
            self.config[Option.SMD_MODEL] = model


class MegaDriveMednafenDriver(MednafenDriver):
    PORTS = SMD_PORTS

    def __init__(self, fsgs):
        super().__init__(fsgs)
        self.helper = MegaDriveHelper(self.options)

    def prepare(self):
        self.init_mega_drive_model()
        self.init_mednafen_crop_from_viewport()
        self.set_mednafen_aspect(4, 3)
        # We do aspect calculation separately. Must not be done twice.
        self.emulator.args.extend(["-md.correct_aspect", "0"])
        # The arguments must be added before the cartridge, which is why
        # we call super().prepare() at the end here.
        super().prepare()

    def init_mega_drive_model(self):
        if self.helper.model() == SMD_MODEL_NTSC_U:
            self.set_model_name("Genesis")
            region = "overseas_ntsc"
        elif self.helper.model() == SMD_MODEL_PAL:
            self.set_model_name("Mega Drive PAL")
            region = "overseas_pal"
        elif self.helper.model() == SMD_MODEL_NTSC_J:
            self.set_model_name("Mega Drive NTSC-J")
            region = "domestic_ntsc"
        else:
            # FIXME: This model might disappear
            self.set_model_name("Mega Drive / Genesis")
            region = "game"
        self.emulator.args.extend(["-md.region", region])

    def init_mednafen_crop_from_viewport(self):
        viewport = self.options[Option.VIEWPORT]
        if viewport:
            if viewport.startswith("0 0 320 240 ="):
                viewport_src, viewport = self.mednafen_viewport()
                self.emulator.env["FSGS_CROP"] = "{},{},{},{}".format(
                    viewport[0], viewport[1], viewport[2], viewport[3])

    def mednafen_system_prefix(self):
        return "md"

    def mednafen_input_mapping(self, port):
        n = port + 1
        return {
            "A": "md.input.port{}.gamepad.a".format(n),
            "B": "md.input.port{}.gamepad.b".format(n),
            "C": "md.input.port{}.gamepad.c".format(n),
            "X": "md.input.port{}.gamepad.x".format(n),
            "Y": "md.input.port{}.gamepad.y".format(n),
            "Z": "md.input.port{}.gamepad.z".format(n),
            "UP": "md.input.port{}.gamepad.up".format(n),
            "DOWN": "md.input.port{}.gamepad.down".format(n),
            "LEFT": "md.input.port{}.gamepad.left".format(n),
            "RIGHT": "md.input.port{}.gamepad.right".format(n),
            "MODE": "md.input.port{}.gamepad.mode".format(n),
            "START": "md.input.port{}.gamepad.start".format(n),
        }

        # FIXME: add PAUSE button to universal gamepad config

    # def game_video_par(self):
    #     # These may not be entirely correct...
    #     if self.is_pal():
    #         return (4 / 3) / (320 / 240)
    #     else:
    #         return (4 / 3) / (320 / 224)

    def game_video_size(self):
        viewport_src, viewport = self.mednafen_viewport()
        if viewport is not None:
            return viewport[2], viewport[3]
        if self.helper.model() == SMD_MODEL_PAL:
            return 320, 240
        else:
            return 320, 224


class MegaDriveHelper:
    def __init__(self, options):
        self.options = options

    def model(self):
        if self.options[Option.SMD_MODEL] == SMD_MODEL_NTSC_U:
            return SMD_MODEL_NTSC_U
        if self.options[Option.SMD_MODEL] == SMD_MODEL_NTSC_J:
            return SMD_MODEL_NTSC_J
        if self.options[Option.SMD_MODEL] == SMD_MODEL_PAL:
            return SMD_MODEL_PAL
        # FIXME: REMOVE?
        return SMD_MODEL_AUTO
