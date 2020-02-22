import hashlib
import os

from fsbc import settings
from fsgs import Option
from fsgs.drivers.messdriver import MessDriver
from fsgs.drivers.mednafendriver import MednafenDriver
from fsgs.drivers.retroarchdriver import RetroArchDriver
from fsgs.platform import Platform
from fsgs.platforms.loader import SimpleLoader


class SuperNintendoPlatformHandler(Platform):
    PLATFORM_NAME = "Super Nintendo"

    def driver(self, fsgc):
        driver = settings.get(Option.SNES_EMULATOR)
        if not driver:
            driver = "mednafen-fs"

        if driver == "mame":
            return MameSnesDriver(fsgc)
        elif driver == "mame-fs":
            return MameFsSnesDriver(fsgc)
        elif driver == "mednafen":
            return MednafenSnesDriver(fsgc)
        elif driver == "mednafen-fs":
            return MednafenFsSnesDriver(fsgc)
        elif driver == "retroarch":
            return RetroArchBsnesDriver(fsgc, "bsnes")
        elif driver == "retroarch/bsnes":
            return RetroArchBsnesDriver(fsgc, "bsnes")
        elif driver == "retroarch/bsnes2014_accuracy":
            return RetroArchBsnesDriver(fsgc, "bsnes2014_accuracy")

        raise Exception("Unknown SNES driver")

    def loader(self, fsgc):
        return SuperNintendoLoader(fsgc)


class SuperNintendoLoader(SimpleLoader):
    def load_extra(self, values):
        self.config[Option.SNES_PORT_1_TYPE] = values["snes_port_1_type"]
        self.config[Option.SNES_PORT_2_TYPE] = values["snes_port_2_type"]
        # self.config[Option.SNES_PORT_3_TYPE] = values["snes_port_3_type"]
        # self.config[Option.SNES_PORT_4_TYPE] = values["snes_port_4_type"]


SNES_CONTROLLER = {
    "type": "gamepad",
    "description": "SNES Controller",
    "mapping_name": "supernintendo",
}
SNES_MOUSE = {"type": "mouse", "description": "SNES Mouse", "mapping_name": ""}
SNES_SUPERSCOPE = {
    "type": "superscope",
    "description": "Super Scope",
    "mapping_name": "",
}

SNES_PORTS = [
    {
        "description": "Port 1",
        "types": [SNES_CONTROLLER, SNES_MOUSE],
        "type_option": "snes_port_1_type",
        "device_option": "snes_port_1",
    },
    {
        "description": "Port 2",
        "types": [SNES_CONTROLLER, SNES_MOUSE, SNES_SUPERSCOPE],
        "type_option": "snes_port_2_type",
        "device_option": "snes_port_2",
    },
]

# noinspection SpellCheckingInspection
SNES_ROMS = {"97e352553e94242ae823547cd853eecda55c20f0": "spc700.rom"}


class MameSnesDriver(MessDriver):
    PORTS = SNES_PORTS

    def __init__(self, fsgc, fsemu=False):
        super().__init__(fsgc, fsemu=fsemu)
        self.helper = SuperNintendoHelper(self.options)
        # self.save_handler.set_save_data_is_emulator_specific(True)
        self.save_handler.set_mame_driver(self.get_mame_driver())

    def prepare(self):
        print("[SNES] MAME driver preparing...")
        super().prepare()
        self.emulator.args.extend(["-cart", self.helper.prepare_rom(self)])

    def get_mame_driver(self):
        # self.helper.set_model_name_from_model(self)
        # if self.helper.model() == SMD_MODEL_NTSC:
        #     return "snes"
        # elif self.helper.model() == SMD_MODEL_PAL:
        #     return "snespal"
        # elif self.helper.model() == SMD_MODEL_NTSC_J:
        #     return "snesj"
        # FIXME
        return "snes"
        raise Exception("Could not determine SNES MAME driver")

    def get_mess_input_mapping(self, _):
        # Button names are listed in MAME UI order: practical, not important.
        return {
            "START": "P#_START",
            "SELECT": "P#_SELECT",
            "UP": "P#_JOYSTICK_UP",
            "DOWN": "P#_JOYSTICK_DOWN",
            "LEFT": "P#_JOYSTICK_LEFT",
            "RIGHT": "P#_JOYSTICK_RIGHT",
            "Y": "P#_BUTTON1",
            "B": "P#_BUTTON2",
            "A": "P#_BUTTON3",
            "X": "P#_BUTTON4",
            "R": "P#_BUTTON5",
            "L": "P#_BUTTON6",
        }

    def get_mess_romset(self):
        driver = self.get_mame_driver()
        if driver == "snes":
            return "snes", SNES_ROMS


class MameFsSnesDriver(MameSnesDriver):
    def __init__(self, fsgc):
        super().__init__(fsgc, fsemu=True)


class MednafenSnesDriver(MednafenDriver):
    PORTS = SNES_PORTS

    def __init__(self, fsgc, fsemu=False):
        super().__init__(fsgc, fsemu=fsemu)
        self.helper = SuperNintendoHelper(self.options)
        self.save_handler.set_save_data_is_emulator_specific(True)

    def prepare(self):
        print("[SNES] Mednafen SNES driver preparing...")
        super().prepare()
        # self.set_mednafen_aspect(4, 3)
        # We do aspect calculation separately. Must not be done twice.

        self.emulator.args.extend(["-snes.input.port1", self.ports[0].type])
        self.emulator.args.extend(["-snes.input.port2", self.ports[1].type])

        self.emulator.args.extend(["-snes.correct_aspect", "1"])
        # FIXME: Input ports configuration
        # FIXME: SNES model
        # ROM path must be added at the end of the argument list
        self.emulator.args.append(self.helper.prepare_rom(self))

        self.emulator.env["FSEMU_MEDNAFEN_CORE"] = "bsnes"

    # def mednafen_aspect_ratio(self):
    #     return 4.0 / 3.0

    def mednafen_input_mapping(self, port):
        n = port + 1
        return {
            "A": "snes.input.port{}.gamepad.a".format(n),
            "B": "snes.input.port{}.gamepad.b".format(n),
            "X": "snes.input.port{}.gamepad.x".format(n),
            "Y": "snes.input.port{}.gamepad.y".format(n),
            "L": "snes.input.port{}.gamepad.l".format(n),
            "R": "snes.input.port{}.gamepad.r".format(n),
            "UP": "snes.input.port{}.gamepad.up".format(n),
            "DOWN": "snes.input.port{}.gamepad.down".format(n),
            "LEFT": "snes.input.port{}.gamepad.left".format(n),
            "RIGHT": "snes.input.port{}.gamepad.right".format(n),
            "SELECT": "snes.input.port{}.gamepad.select".format(n),
            "START": "snes.input.port{}.gamepad.start".format(n),
        }

    def mednafen_system_prefix(self):
        return "snes"

    def game_video_par(self):
        # These may not be entirely correct...
        # if self.is_pal():
        #     return (4 / 3) / (256 / 239)
        # else:
        #     return (4 / 3) / (256 / 224)
        size = self.game_video_size()
        return (4 / 3) / (size[0] / size[1])

    def game_video_size(self):
        if self.is_pal():
            size = (256, 239)
        else:
            size = (256, 224)
        return size

    def get_game_file(self, config_key="cartridge_slot"):
        return None


class MednafenFsSnesDriver(MednafenSnesDriver):
    def __init__(self, fsgc):
        super().__init__(fsgc, fsemu=True)


class RetroArchBsnesDriver(RetroArchDriver):
    PORTS = SNES_PORTS

    def __init__(self, fsgc, libretro_core):
        # libretro_core = "bsnes"
        # libretro_core = "bsnes2014_accuracy"
        # libretro_core =
        # save_name = "RetroArch/bsnes2014_accuracy"
        if libretro_core == "bsnes2014_accuracy":
            save_name = "BSnes2014-LR"
        elif libretro_core == "bsnes":
            save_name = "BSnes-LR"
        else:
            raise Exception("Unknown SNES libretro core")
        super().__init__(fsgc, libretro_core, save_name)
        self.helper = SuperNintendoHelper(self.options)

    def prepare(self):
        super().prepare()
        self.emulator.args.append(self.helper.prepare_rom(self))

        # Workaround for Intel / MESA on Linux (FIXME: Should perhaps check if
        # Intel / MESA driver is in use first...
        # https://github.com/gonetz/GLideN64/issues/454
        # self.emulator.env["MESA_GL_VERSION_OVERRIDE"] = "3.3COMPAT"
        # self.emulator.env["MESA_GLSL_VERSION_OVERRIDE"] = "420"

    def retroarch_input_mapping(self, port):
        input_mapping = {
            "A": "input_player{n}_a",
            "B": "input_player{n}_b",
            "X": "input_player{n}_x",
            "Y": "input_player{n}_y",
            "L": "input_player{n}_l",
            "R": "input_player{n}_r",
            "UP": "input_player{n}_up",
            "DOWN": "input_player{n}_down",
            "LEFT": "input_player{n}_left",
            "RIGHT": "input_player{n}_right",
            "SELECT": "input_player{n}_select",
            "START": "input_player{n}_start",
        }
        return {k: v.format(n=port + 1) for k, v in input_mapping.items()}


class SuperNintendoHelper:
    def __init__(self, options):
        self.options = options

    # FIXME: Shared, move into common module (find all occurrences)
    def prepare_rom(self, driver):
        file_uri = self.options[Option.CARTRIDGE_SLOT]
        # file_uri = os.path.expanduser("~/Desktop/240pSuite.sfc")
        input_stream = driver.fsgc.file.open(file_uri)
        _, ext = os.path.splitext(file_uri)
        return self.prepare_rom_with_stream(driver, input_stream, ext)

    # FIXME: Shared, move into common module (find all occurrences)
    def prepare_rom_with_stream(self, driver, input_stream, ext):
        sha1_obj = hashlib.sha1()
        path = driver.temp_file("rom" + ext).path
        with open(path, "wb") as f:
            while True:
                data = input_stream.read(65536)
                if not data:
                    break
                f.write(data)
                sha1_obj.update(data)
        new_path = os.path.join(
            os.path.dirname(path), sha1_obj.hexdigest()[:8].upper() + ext
        )
        os.rename(path, new_path)
        return new_path
