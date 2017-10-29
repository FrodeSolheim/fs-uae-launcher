from fsbc import settings
from fsgs.drivers.mednafendriver import MednafenDriver
from fsgs.drivers.retroarchdriver import RetroArchDriver
from fsgs.option import Option
from fsgs.platform import Platform
from fsgs.platforms.loader import SimpleLoader

SMD_MODEL_NTSC = "ntsc"
SMD_MODEL_NTSC_J = "ntsc-j"
SMD_MODEL_PAL = "pal"
# FIXME: REMOVE MODEL AUTO? It makes it difficult to predict video size
# without inspecting ROM file.
# SMD_MODEL_AUTO = "auto"
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
        emulator = settings.get(Option.SMD_EMULATOR)

        if emulator in ["retroarch", "retroarch-genesis-plus-gx"]:
            return MegaDriveRetroArchDriver(fsgc)
        # elif driver in ["mame", "mess"]:
        #     return MessNesDriver(fsgc)
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
                model = SMD_MODEL_NTSC
            elif "europe" in variant or "australia" in variant:
                model = SMD_MODEL_PAL
            elif "japan" in variant:
                model = SMD_MODEL_NTSC_J
            else:
                # FIXME: Remove?
                # model = SMD_MODEL_AUTO
                model = SMD_MODEL_NTSC
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
        self.helper.set_model_name_from_model(self)
        if self.helper.model() == SMD_MODEL_NTSC:
            region = "overseas_ntsc"
        elif self.helper.model() == SMD_MODEL_PAL:
            region = "overseas_pal"
        elif self.helper.model() == SMD_MODEL_NTSC_J:
            region = "domestic_ntsc"
        else:
            # FIXME: This model might disappear
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


class MegaDriveRetroArchDriver(RetroArchDriver):
    PORTS = SMD_PORTS

    def __init__(self, fsgc):
        super().__init__(
            fsgc, "genesis_plus_gx_libretro", "RetroArch/Genesis-Plus-Gx")
        self.helper = MegaDriveHelper(self.options)

    def prepare(self):
        super().prepare()
        hw = "mega drive / genesis"
        region = self.init_mega_drive_model()
        with self.open_retroarch_core_options() as f:
            f.write("genesis_plus_gx_system_hw = \"{}\"\n".format(hw))
            f.write("genesis_plus_gx_region_detect = {}\n".format(region))

        #     viewport = self.options[Option.VIEWPORT]
        #     if viewport == "0 0 256 240 = 0 0 256 240":
        #         overscan_h, overscan_v = "disabled", "disabled"
        #     # elif viewport == "0 0 256 240 = 0 8 256 224":
        #     #     return 256, 224
        #     elif viewport == "0 0 256 240 = 8 0 240 240":
        #         overscan_h, overscan_v = "enabled", "disabled"
        #     elif viewport == "0 0 256 240 = 8 8 240 224":
        #         overscan_h, overscan_v = "enabled", "enabled"
        #     else:
        #         overscan_h, overscan_v = "disabled", "enabled"
        #     f.write("nestopia_overscan_h = {}\n".format(overscan_h))
        #     f.write("nestopia_overscan_v = {}\n".format(overscan_v))
        # self.emulator.args.append(self.helper.prepare_rom(self))
        self.emulator.args.append(self.get_game_file())

    def init_mega_drive_model(self):
        self.helper.set_model_name_from_model(self)
        if self.helper.model() == SMD_MODEL_NTSC:
            return "ntsc-u"
        elif self.helper.model() == SMD_MODEL_PAL:
            return "pal"
        elif self.helper.model() == SMD_MODEL_NTSC_J:
            return "ntsc-j"
        return "ntsc-u"

    def game_video_size(self):
        # # FIXME: Account for horizontal overscan
        # # FIXME: Account for vertical overscan
        #
        # viewport = self.options[Option.VIEWPORT]
        # if viewport == "0 0 256 240 = 0 0 256 240":
        #     return 256, 240
        # # elif viewport == "0 0 256 240 = 0 8 256 224":
        # #     return 256, 224
        # elif viewport == "0 0 256 240 = 8 0 240 240":
        #     return 240, 240
        # elif viewport == "0 0 256 240 = 8 8 240 224":
        #     return 240, 224
        # else:
        #     return 256, 224
        return 320, 224

    def retroarch_input_mapping(self, port):
        n = port + 1
        return {
            "A": "input_player{}_a".format(n),
            "B": "input_player{}_b".format(n),
            "UP": "input_player{}_up".format(n),
            "DOWN": "input_player{}_down".format(n),
            "LEFT": "input_player{}_left".format(n),
            "RIGHT": "input_player{}_right".format(n),
            "SELECT": "input_player{}_select".format(n),
            "START": "input_player{}_start".format(n),
        }

    # def window_size(self):
    #     return 256, 224


class MegaDriveHelper:
    def __init__(self, options):
        self.options = options

    def model(self):
        if self.options[Option.SMD_MODEL] == SMD_MODEL_NTSC:
            return SMD_MODEL_NTSC
        if self.options[Option.SMD_MODEL] == SMD_MODEL_NTSC_J:
            return SMD_MODEL_NTSC_J
        if self.options[Option.SMD_MODEL] == SMD_MODEL_PAL:
            return SMD_MODEL_PAL
        # FIXME: REMOVE?
        # return SMD_MODEL_AUTO
        return SMD_MODEL_NTSC

    def set_model_name_from_model(self, driver):
        model = self.model()
        if model == SMD_MODEL_NTSC:
            driver.set_model_name("Genesis")
        elif model == SMD_MODEL_PAL:
            driver.set_model_name("Mega Drive PAL")
        elif model == SMD_MODEL_NTSC_J:
            driver.set_model_name("Mega Drive NTSC-J")
        # else:
        #     # FIXME: This model might disappear
        #     # driver.set_model_name("Mega Drive / Genesis")
        #     assert False
