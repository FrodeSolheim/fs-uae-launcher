import hashlib
import os
import shutil
from binascii import unhexlify

from fsbc import settings
from fsgamesys.drivers.mednafendriver import MednafenDriver
from fsgamesys.drivers.messdriver import MessDriver
from fsgamesys.drivers.retroarchdriver import RetroArchDriver
from fsgamesys.options.option import Option
from fsgamesys.platforms.loader import SimpleLoader
from fsgamesys.platforms.platform import Platform

NES_PLATFORM_ID = "nes"
NES_PLATFORM_NAME = "Nintendo"
NES_MODEL_NTSC = "ntsc"
NES_MODEL_PAL = "pal"
NES_MODEL_FAMICOM = "ntsc-j"
NES_CONTROLLER_TYPE = "gamepad"
NES_CONTROLLER = {
    "type": NES_CONTROLLER_TYPE,
    "description": "NES Gamepad",
    "mapping_name": "nintendo",
}
NES_ZAPPER_CONTROLLER_TYPE = "zapper"
NES_ZAPPER_CONTROLLER = {
    "type": NES_ZAPPER_CONTROLLER_TYPE,
    "description": "NES Zapper",
    "mapping_name": "",
}
NES_ARKANOID_CONTROLLER_TYPE = "arkanoid"
NES_ARKANOID_CONTROLLER = {
    "type": NES_ARKANOID_CONTROLLER_TYPE,
    "description": "Arkanoid Paddle",
    "mapping_name": "",
}
NO_CONTROLLER_TYPE = "none"
NO_CONTROLLER = {
    "type": NO_CONTROLLER_TYPE,
    "description": "None",
    "mapping_name": "",
}

NES_PORTS = [
    {
        "description": "Port 1",
        "types": [
            NES_CONTROLLER,
            NES_ZAPPER_CONTROLLER,
            NES_ARKANOID_CONTROLLER,
            NO_CONTROLLER,
        ],
        "type_option": "nes_port_1_type",
        "device_option": "nes_port_1",
    },
    {
        "description": "Port 2",
        "types": [
            NES_CONTROLLER,
            NES_ZAPPER_CONTROLLER,
            NES_ARKANOID_CONTROLLER,
            NO_CONTROLLER,
        ],
        "type_option": "nes_port_2_type",
        "device_option": "nes_port_2",
    },
    {
        "description": "Port 3",
        "types": [NES_CONTROLLER, NO_CONTROLLER],
        "type_option": "nes_port_3_type",
        "device_option": "nes_port_3",
    },
    {
        "description": "Port 4",
        "types": [NES_CONTROLLER, NO_CONTROLLER],
        "type_option": "nes_port_4_type",
        "device_option": "nes_port_4",
    },
]


class NintendoPlatform(Platform):
    PLATFORM_NAME = NES_PLATFORM_NAME

    @staticmethod
    def driver(fsgc):
        driver = settings.get(Option.NES_EMULATOR)
        if not driver:
            driver = "mednafen-fs"

        # if driver == "higan":
        #     return HiganNesDriver(fsgc)
        if driver == "mame":
            return MameNesDriver(fsgc)
        elif driver == "mame-fs":
            return MameFsNesDriver(fsgc)
        elif driver == "mednafen":
            return MednafenNesDriver(fsgc)
        elif driver == "mednafen-fs":
            return MednafenFsNesDriver(fsgc)
        elif driver == "retroarch":
            return RetroArchMesenDriver(fsgc)
        elif driver == "retroarch/mesen":
            return RetroArchMesenDriver(fsgc)
        elif driver == "retroarch/nestopia":
            return RetroArchNestopiaDriver(fsgc)

        return None

    @staticmethod
    def loader(fsgc):
        return NintendoLoader(fsgc)

    @staticmethod
    def name():
        return "Nintendo"


class NintendoLoader(SimpleLoader):
    def load_extra(self, values):
        self.config[Option.NES_MODEL] = values["nes_model"]
        self.config[Option.NES_INES_HEADER] = values["ines_header"]
        self.config[Option.NES_PORT_1_TYPE] = values["nes_port_1_type"]
        self.config[Option.NES_PORT_2_TYPE] = values["nes_port_2_type"]
        self.config[Option.NES_PORT_3_TYPE] = values["nes_port_3_type"]
        self.config[Option.NES_PORT_4_TYPE] = values["nes_port_4_type"]

        # FIXME: Temporary
        if self.config[Option.NES_MODEL] == "famicom":
            self.config[Option.NES_MODEL] = NES_MODEL_FAMICOM


class NesController:
    # def __init__(self):
    #     self.descriptyion = ""

    @property
    @staticmethod
    def description():
        return "Controller"

    @staticmethod
    def gamepad_mapping(port):
        mapping = {
            Controller.A: NES_GAMEPAD_B,
            Controller.B: NES_GAMEPAD_A,
            Controller.X: NES_GAMEPAD_A,
            Controller.Y: NES_GAMEPAD_B,
            Controller.DPLEFT: NES_GAMEPAD_LEFT,
            Controller.DPRIGHT: NES_GAMEPAD_RIGHT,
            Controller.DPUP: NES_GAMEPAD_UP,
            Controller.DPDOWN: NES_GAMEPAD_DOWN,
            Controller.LEFTXNEG: NES_GAMEPAD_LEFT,
            Controller.LEFTXPOS: NES_GAMEPAD_RIGHT,
            Controller.LEFTYNEG: NES_GAMEPAD_UP,
            Controller.LEFTYPOS: NES_GAMEPAD_DOWN,
            Controller.START: NES_GAMEPAD_START,
            Controller.BACK: NES_GAMEPAD_SELECT,
        }
        return mapping

    @staticmethod
    def keyboard_mapping(port):
        mapping = {
            Key.C: NES_GAMEPAD_A,
            Key.X: NES_GAMEPAD_B,
            Key.LEFT: NES_GAMEPAD_LEFT,
            Key.RIGHT: NES_GAMEPAD_RIGHT,
            Key.UP: NES_GAMEPAD_UP,
            Key.DOWN: NES_GAMEPAD_DOWN,
            Key.RETURN: NES_GAMEPAD_START,
            Key.SPACE: NES_GAMEPAD_SELECT,
        }
        return mapping


class NesPort:
    def __init__(self, name):
        self.number = 0
        self.name = name
        self.types = []
        self.index = 0
        self.device = None
        # Name of config option for device type
        self.type_option = ""
        # Name of config option for device
        self.device_option = ""

        # FIXME: remove
        self.device_id = None
        self.device_config = None
        self.mapping_name_override = None

    @property
    def type(self):
        return self.types[self.index]["type"]

    @property
    def mapping_name(self):
        if self.mapping_name_override:
            return self.mapping_name_override
        return self.types[self.index]["mapping_name"]

    @property
    def description(self):
        return self.types[self.index]["description"]


# class HiganNesDriver(GameDriver):
#     PORTS = NES_PORTS

#     def __init__(self, fsgs):
#         super().__init__(fsgs)
#         self.emulator = Emulator("higan")
#         self.emulator.allow_system_emulator = True
#         self.helper = NintendoHelper(self.options)

#     def prepare(self):
#         if self.use_fullscreen():
#             self.emulator.args.append("--fullscreen")

#         # model = self.helper.nes_model()

#         rom_path = self.get_game_file()
#         self.helper.fix_ines_rom(rom_path)
#         self.emulator.args.extend([rom_path])


class MameNesDriver(MessDriver):
    PORTS = NES_PORTS

    def __init__(self, fsgc, fsemu=False):
        super().__init__(fsgc, fsemu=fsemu)
        # self.save_handler.set_save_data_is_emulator_specific()
        self.save_handler.set_mame_driver(self.mame_driver())

        # FIXME...
        self.options["viewport"] = ""

    def prepare(self):
        print("[NES] MAME driver preparing...")
        super().prepare()
        self.emulator.args.extend(["-cart", nes_prepare_rom(self)])

    def mame_driver(self):
        model = nes_model(self.options)
        if model == NES_MODEL_PAL:
            return "nespal"
        elif model == NES_MODEL_NTSC:
            return "nes"
        elif model == NES_MODEL_FAMICOM:
            return "famicom"
        raise Exception("Could not determine NES MAME driver")

    def mess_input_mapping(self, _):
        # Button names are listed in MAME UI order: practical, not important.
        # FIXME: Are they?
        return {
            "START": "P#_START",
            "SELECT": "P#_SELECT",
            "UP": "P#_JOYSTICK_UP",
            "DOWN": "P#_JOYSTICK_DOWN",
            "LEFT": "P#_JOYSTICK_LEFT",
            "RIGHT": "P#_JOYSTICK_RIGHT",
            "B": "P#_BUTTON1",
            "A": "P#_BUTTON2",
        }

    # def mess_offset_and_scale(self):
    #     # if self.get_romset() == "nespal":
    #     #     return 0.0, 0.0, 1.082, 1.250
    #     # return 0.0, 0.0, 1.072, 1.164
    #     return 0.0, 0.0, 1.072, 1.100

    def mess_romset(self):
        driver = self.mame_driver()
        if driver == "famicom":
            return "famicom", {}
        elif driver == "nespal":
            return "nespal", {}
        else:
            return "nes", {}


class MameFsNesDriver(MameNesDriver):
    def __init__(self, fsgc):
        super().__init__(fsgc, fsemu=True)


class MednafenNesDriver(MednafenDriver):
    PORTS = NES_PORTS

    def __init__(self, fsgc, fsemu=False):
        super().__init__(fsgc, fsemu=fsemu)
        # self.save_handler.set_save_data_is_emulator_specific()
        self.save_handler.set_srm_alias(".sav")

        # self.helper = NintendoHelper(self.options)
        # port_2 = self.options[Option.NES_PORT_2_TYPE]
        # if port_2 == NES_ARKANOID_CONTROLLER_TYPE:
        #     print("[DRIVER] NES Port 2 type:", port_2)
        #     for i, t in enumerate(self.ports[1].types):
        #         if t["type"] == NES_ARKANOID_CONTROLLER_TYPE:
        #             self.ports[1].index = i
        #             break
        port_3 = self.options[Option.NES_PORT_3_TYPE]
        port_4 = self.options[Option.NES_PORT_4_TYPE]
        if not port_3 and not port_4:
            # Remove the last two input ports - not in use.
            self.ports[2:4] = []

    def prepare(self):
        print("[DRIVER] Mednafen NES driver preparing...")
        super().prepare()
        pfx = self.mednafen_system_prefix()

        self.emulator.args.extend(
            ["-{}.input.port1".format(pfx), self.ports[0].type]
        )
        self.emulator.args.extend(
            ["-{}.input.port2".format(pfx), self.ports[1].type]
        )

        model = nes_model(self.options)
        if model == NES_MODEL_PAL:
            self.set_model_name("Nintendo (PAL)")
            self.emulator.args.extend(["-{}.pal".format(pfx), "1"])
        else:
            if model == NES_MODEL_FAMICOM:
                self.set_model_name("Famicom")
            else:
                self.set_model_name("Nintendo (NTSC)")
            self.emulator.args.extend(["-{}.pal".format(pfx), "0"])
        self.emulator.args.extend(["-{}.fnscan".format(pfx), "0"])

        # self.emulator.env["FSGS_ASPECT"] = "4/3"
        # self.emulator.env["FSEMU_ASPECT"] = "4/3"

        overscan_h, overscan_v = nes_overscan(self.options)
        self.emulator.args.extend(
            ["-nes.clipsides", "0" if overscan_h else "1"]
        )
        if overscan_v:
            pal_first_y = 0
            pal_last_y = 239
            ntsc_first_y = 0  # 8
            ntsc_last_y = 239  # 231
        else:
            pal_first_y = 8
            ntsc_first_y = 8
            pal_last_y = 231
            ntsc_last_y = 231
        self.emulator.args.extend(["-nes.slstart", str(ntsc_first_y)])
        self.emulator.args.extend(["-nes.slend", str(ntsc_last_y)])
        self.emulator.args.extend(["-nes.slstartp", str(pal_first_y)])
        self.emulator.args.extend(["-nes.slendp", str(pal_last_y)])

        # viewport = self.options[Option.VIEWPORT]
        # # FIXME
        # viewport = ""

        # if viewport == "0 0 256 240 = 0 0 256 240":
        #     self.emulator.env["FSGS_CROP"] = "0,0,256,240"
        # # elif viewport == "0 0 256 240 = 0 8 256 224":
        # #     self.emulator.env["FSGS_CROP"] = "0,8,256,224"
        # elif viewport == "0 0 256 240 = 8 0 240 240":
        #     self.emulator.env["FSGS_CROP"] = "8,0,240,240"
        # elif viewport == "0 0 256 240 = 8 8 240 224":
        #     self.emulator.env["FSGS_CROP"] = "8,8,240,224"
        # else:
        #     self.emulator.env["FSGS_CROP"] = "0,8,256,224"

        # x, y, w, h = 0, 0, 256, 240
        # if not overscan_h:
        #     x += 8
        #     w -= 16
        # if not overscan_v:
        #     y += 8
        #     h -= 16

        # self.emulator.env["FSGS_CROP"] = "{},{},{},{}".format(x, y, w, h)

        nes_prepare_palette(
            self.options,
            os.path.join(
                self.palette_dir.path,
                "nes-pal.pal" if nes_is_pal(self.options) else "nes.pal",
            ),
        )

        self.emulator.args.append(nes_prepare_rom(self))

    def finish(self):
        print("[DRIVER] Mednafen NES Driver finishing...")
        super().finish()

    def mednafen_input_mapping(self, port):
        n = port + 1
        return {
            "A": "nes.input.port{}.gamepad.a".format(n),
            "B": "nes.input.port{}.gamepad.b".format(n),
            "UP": "nes.input.port{}.gamepad.up".format(n),
            "DOWN": "nes.input.port{}.gamepad.down".format(n),
            "LEFT": "nes.input.port{}.gamepad.left".format(n),
            "RIGHT": "nes.input.port{}.gamepad.right".format(n),
            "SELECT": "nes.input.port{}.gamepad.select".format(n),
            "START": "nes.input.port{}.gamepad.start".format(n),
        }

    def mednafen_rom_extensions(self):
        return [".nes"]

    def mednafen_system_prefix(self):
        return "nes"

    def game_video_par(self):
        size = self.game_video_size()
        return (4 / 3) / (size[0] / size[1])

    def game_video_size(self):
        # FIXME: overscan
        size = (256, 240)

        # # FIXME
        # if nes_is_pal(self.options):
        #     size = (256, 240)
        # else:
        #     size = (256, 224)
        # # if self.nes_clip_sides():
        # #     size = (size[0] - 16, size[1])

        return size

    def get_game_file(self, config_key="cartridge_slot"):
        # path = super().get_game_file()
        #
        # # FIXME: Replace and do in one go without going via super
        # input_stream = self.fsgc.file.open(path)
        # _, ext = os.path.splitext(path)
        # return self.prepare_rom_with_stream(self, input_stream, ext)
        # return self.helper.prepare_rom(self)
        return None


class MednafenFsNesDriver(MednafenNesDriver):
    def __init__(self, fsgc):
        super().__init__(fsgc, fsemu=True)


class RetroArchNesDriver(RetroArchDriver):
    PORTS = NES_PORTS

    def __init__(self, fsgc, libretro_core, state_dir_name, remap_core):
        super().__init__(fsgc, libretro_core, state_dir_name)
        # self.save_handler.set_save_data_is_emulator_specific()

        self.retroarch_remap_core = remap_core

    def controller_for_port(self, port):
        print("[NES] Get controller for port index", port.index)
        return NesController()


class RetroArchMesenDriver(RetroArchNesDriver):
    def __init__(self, fsgc):
        super().__init__(fsgc, "mesen", "Mesen-LR", "Mesen")

    def prepare(self):
        core_options = {}

        # self.set_model_name({
        #     NES_MODEL_PAL: "Nintendo (PAL)",
        #     NES_MODEL_NTSC: "Nintendo (NTSC)",
        #     NES_MODEL_FAMICOM: "Famicom",
        # }[nes_model(self.options)])

        if nes_prepare_palette(
            self.options,
            os.path.join(self.system_dir.path, "MesenPalette.pal"),
        ):
            core_options["mesen_palette"] = "Custom"

        core_options["mesen_region"] = {
            NES_MODEL_PAL: "PAL",
            NES_MODEL_NTSC: "NTSC",
            NES_MODEL_FAMICOM: "Auto",  # or NTSC?
        }[nes_model(self.options)]

        overscan_h, overscan_v = nes_overscan(self.options)
        core_options["mesen_overscan_horizontal"] = (
            "None" if overscan_h else "8px"
        )
        core_options["mesen_overscan_vertical"] = (
            "None" if overscan_v else "8px"
        )

        super().prepare(
            libretro_core_options=core_options,
            libretro_content_factory=nes_rom_factory(self),
        )

    def retropad_mapping_for_port(self, port):
        mapping = {
            RETRO_DEVICE_ID_JOYPAD_LEFT: NES_GAMEPAD_LEFT,
            RETRO_DEVICE_ID_JOYPAD_UP: NES_GAMEPAD_UP,
            RETRO_DEVICE_ID_JOYPAD_DOWN: NES_GAMEPAD_DOWN,
            RETRO_DEVICE_ID_JOYPAD_RIGHT: NES_GAMEPAD_RIGHT,
            RETRO_DEVICE_ID_JOYPAD_B: NES_GAMEPAD_A,
            RETRO_DEVICE_ID_JOYPAD_Y: NES_GAMEPAD_B,
            RETRO_DEVICE_ID_JOYPAD_A: NES_GAMEPAD_A_TURBO,
            RETRO_DEVICE_ID_JOYPAD_X: NES_GAMEPAD_B_TURBO,
            RETRO_DEVICE_ID_JOYPAD_SELECT: NES_GAMEPAD_SELECT,
            RETRO_DEVICE_ID_JOYPAD_START: NES_GAMEPAD_START,
        }
        if port.index == 0:
            mapping.update(
                {
                    # FIXME: "(FDS) Insert Next Disk"
                    RETRO_DEVICE_ID_JOYPAD_L: NES_DISK_EJECT,
                    RETRO_DEVICE_ID_JOYPAD_R: NES_DISK_SIDE_CHANGE,
                    RETRO_DEVICE_ID_JOYPAD_L2: NES_COIN_1,
                    RETRO_DEVICE_ID_JOYPAD_R2: NES_COIN_2,
                    RETRO_DEVICE_ID_JOYPAD_L3: NES_MICROPHONE,
                }
            )
        return mapping


class RetroArchNestopiaDriver(RetroArchNesDriver):
    def __init__(self, fsgc):
        super().__init__(fsgc, "nestopia", "Nestopia-LR", "Nestopia")

    def prepare(self):
        core_options = {}

        # self.set_model_name({
        #     NES_MODEL_PAL: "Nintendo (PAL)",
        #     NES_MODEL_NTSC: "Nintendo (NTSC)",
        #     NES_MODEL_FAMICOM: "Famicom",
        # }[nes_model(self.options)])

        if nes_prepare_palette(
            self.options, os.path.join(self.system_dir.path, "custom.pal")
        ):
            core_options["nestopia_palette"] = "custom"

        core_options["nestopia_favored_system"] = {
            NES_MODEL_PAL: "pal",
            NES_MODEL_NTSC: "ntsc",
            NES_MODEL_FAMICOM: "famicom",
        }[nes_model(self.options)]

        overscan_h, overscan_v = nes_overscan(self.options)
        core_options["nestopia_overscan_h"] = (
            "disabled" if overscan_h else "enabled"
        )
        core_options["nestopia_overscan_v"] = (
            "disabled" if overscan_v else "enabled"
        )

        super().prepare(
            libretro_core_options=core_options,
            libretro_content_factory=nes_rom_factory(self),
        )
        # self.emulator.args.append(self.helper.prepare_rom(self))

    def retropad_mapping_for_port(self, port):
        mapping = {
            RETRO_DEVICE_ID_JOYPAD_LEFT: NES_GAMEPAD_LEFT,
            RETRO_DEVICE_ID_JOYPAD_UP: NES_GAMEPAD_UP,
            RETRO_DEVICE_ID_JOYPAD_DOWN: NES_GAMEPAD_DOWN,
            RETRO_DEVICE_ID_JOYPAD_RIGHT: NES_GAMEPAD_RIGHT,
            RETRO_DEVICE_ID_JOYPAD_B: NES_GAMEPAD_B,
            RETRO_DEVICE_ID_JOYPAD_A: NES_GAMEPAD_A,
            RETRO_DEVICE_ID_JOYPAD_X: NES_GAMEPAD_A_TURBO,
            RETRO_DEVICE_ID_JOYPAD_Y: NES_GAMEPAD_B_TURBO,
            RETRO_DEVICE_ID_JOYPAD_L: NES_DISK_SIDE_CHANGE,
            RETRO_DEVICE_ID_JOYPAD_R: NES_DISK_EJECT,
            RETRO_DEVICE_ID_JOYPAD_L3: NES_MICROPHONE,
            RETRO_DEVICE_ID_JOYPAD_SELECT: NES_GAMEPAD_SELECT,
            RETRO_DEVICE_ID_JOYPAD_START: NES_GAMEPAD_START,
        }
        if port.index == 0:
            mapping.update(
                {
                    RETRO_DEVICE_ID_JOYPAD_L2: NES_COIN_1,
                    RETRO_DEVICE_ID_JOYPAD_R2: NES_COIN_2,
                }
            )
        return mapping


def nes_model(options):
    model = options.get(Option.NES_MODEL, "")
    if model in ["", "ntsc"]:
        return NES_MODEL_NTSC
    elif model == "pal":
        return NES_MODEL_PAL
    elif model == "ntsc-j":
        return NES_MODEL_FAMICOM
    elif model == "famicom":
        return NES_MODEL_FAMICOM
    else:
        raise Exception("Invalid NES model:", model)


def nes_is_pal(options):
    return nes_model(options) == NES_MODEL_PAL


def nes_overscan(options):
    viewport = options[Option.VIEWPORT]
    if viewport == "0 0 256 240 = 0 0 256 240":
        overscan_h, overscan_v = True, True
    elif viewport == "0 0 256 240 = 0 8 256 224":
        overscan_h, overscan_v = True, False
    elif viewport == "0 0 256 240 = 8 0 240 240":
        overscan_h, overscan_v = False, True
    elif viewport == "0 0 256 240 = 8 8 240 224":
        overscan_h, overscan_v = False, False
    else:
        overscan_h, overscan_v = True, True
    # FIXME: Overriding (disabling) overscan for now
    overscan_h, overscan_v = False, False
    # overscan_h, overscan_v = True, True
    return overscan_h, overscan_v


def nes_prepare_palette(options, palette_dest):
    palette_file = options[Option.NES_PALETTE_FILE]
    if palette_file:
        if os.path.exists(palette_file):
            shutil.copy(palette_file, palette_dest)
            return palette_dest
    # When disabled, remove existing palette, if any.
    if os.path.exists(palette_dest):
        os.remove(palette_dest)
    return None


def nes_prepare_rom(driver):
    file_uri = driver.options[Option.CARTRIDGE_SLOT]
    input_stream = driver.fsgc.file.open(file_uri)
    _, ext = os.path.splitext(file_uri)
    return nes_prepare_rom_with_stream(driver, input_stream, ext)


def nes_prepare_rom_with_stream(driver, input_stream, ext):
    # This should not be necessary for files found via the file database
    # and the online game database, but could be necessary for manually
    # loaded files.
    data = input_stream.read(16)
    if len(data) == 16 and data.startswith(b"NES\x1a"):
        print("[DRIVER] Stripping iNES header")
        data = None
    else:
        # No iNES header, include data
        pass

    sha1_obj = hashlib.sha1()

    path = driver.temp_file("rom" + ext).path
    with open(path, "wb") as f:
        header = driver.options[Option.NES_INES_HEADER]
        if header:
            assert len(header) == 16 * 2
            f.write(unhexlify(header))
            # We're excluding header data from checksum to avoid checking
            # changing if we update the iNES header
            # sha1_obj.update(unhexlify(header))
        if data is not None:
            f.write(data)
            sha1_obj.update(data)
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


def nes_rom_factory(driver):
    def factory_function():
        return nes_prepare_rom(driver)

    return factory_function


# def nes_rom_factory():
#     def factory_function(driver):
#         return nes_prepare_rom(driver)
#     return factory_function


RETRO_DEVICE_ID_JOYPAD_B = 0
RETRO_DEVICE_ID_JOYPAD_Y = 1
RETRO_DEVICE_ID_JOYPAD_SELECT = 2
RETRO_DEVICE_ID_JOYPAD_START = 3
RETRO_DEVICE_ID_JOYPAD_UP = 4
RETRO_DEVICE_ID_JOYPAD_DOWN = 5
RETRO_DEVICE_ID_JOYPAD_LEFT = 6
RETRO_DEVICE_ID_JOYPAD_RIGHT = 7
RETRO_DEVICE_ID_JOYPAD_A = 8
RETRO_DEVICE_ID_JOYPAD_X = 9
RETRO_DEVICE_ID_JOYPAD_L = 10
RETRO_DEVICE_ID_JOYPAD_R = 11
RETRO_DEVICE_ID_JOYPAD_L2 = 12
RETRO_DEVICE_ID_JOYPAD_R2 = 13
RETRO_DEVICE_ID_JOYPAD_L3 = 14
RETRO_DEVICE_ID_JOYPAD_R3 = 15

NES_GAMEPAD_LEFT = "left"
NES_GAMEPAD_RIGHT = "right"
NES_GAMEPAD_UP = "up"
NES_GAMEPAD_DOWN = "down"
NES_GAMEPAD_A = "a"
NES_GAMEPAD_B = "b"
NES_GAMEPAD_A_TURBO = "a_turbo"
NES_GAMEPAD_B_TURBO = "b_turbo"
NES_GAMEPAD_START = "start"
NES_GAMEPAD_SELECT = "select"

NES_DISK_SIDE_CHANGE = "disk_side_change"
NES_DISK_EJECT = "disk_eject"
NES_COIN_1 = "coin_1"
NES_COIN_2 = "coin_2"
NES_MICROPHONE = "microphone"

# SDL_CONTROLLER_BUTTON_A
# SDL_CONTROLLER_BUTTON_B
# SDL_CONTROLLER_BUTTON_X
# SDL_CONTROLLER_BUTTON_Y
# SDL_CONTROLLER_BUTTON_BACK
# SDL_CONTROLLER_BUTTON_GUIDE
# SDL_CONTROLLER_BUTTON_START
# SDL_CONTROLLER_BUTTON_LEFTSTICK
# SDL_CONTROLLER_BUTTON_RIGHTSTICK
# SDL_CONTROLLER_BUTTON_LEFTSHOULDER
# SDL_CONTROLLER_BUTTON_RIGHTSHOULDER
# SDL_CONTROLLER_BUTTON_DPAD_UP
# SDL_CONTROLLER_BUTTON_DPAD_DOWN
# SDL_CONTROLLER_BUTTON_DPAD_LEFT
# SDL_CONTROLLER_BUTTON_DPAD_RIGHT

# SDL_CONTROLLER_AXIS_LEFTX
# SDL_CONTROLLER_AXIS_LEFTY
# SDL_CONTROLLER_AXIS_RIGHTX
# SDL_CONTROLLER_AXIS_RIGHTY
# SDL_CONTROLLER_AXIS_TRIGGERLEFT
# SDL_CONTROLLER_AXIS_TRIGGERRIGHT

# Controller,a:b1,
# b:b2,
# y:b3,
# x:b0,
# start:b9,
# guide:b12,
# back:b8,
# dpup:h0.1,dpleft:h0.8,dpdown:h0.4,dpright:h0.2,
# leftshoulder:b4,rightshoulder:b5,
# leftstick:b10,rightstick:b11,
# leftx:a0,lefty:a1,rightx:a2,righty:a3,lefttrigger:b6,righttrigger:b7"

CONTROLLER_A = "a"
CONTROLLER_B = "b"
CONTROLLER_X = "x"
CONTROLLER_Y = "y"
CONTROLLER_START = "start"
CONTROLLER_GUIDE = "guide"
CONTROLLER_BACK = "back"
CONTROLLER_DPUP = "dpup"
CONTROLLER_DPLEFT = "dpleft"
CONTROLLER_DPRIGHT = "dpright"
CONTROLLER_DPDOWN = "dpdown"
CONTROLLER_LEFTSHOULDER = "leftshoulder"
CONTROLLER_RIGHTSHOULDER = "rightshoulder"
CONTROLLER_LEFTSTICK = "leftstick"
CONTROLLER_RIGHTSTICK = "rightstick"
CONTROLLER_LEFTX = "leftx"
CONTROLLER_LEFTY = "lefty"
CONTROLLER_RIGHTX = "rightx"
CONTROLLER_RIGHTY = "righty"
CONTROLLER_LEFTTRIGGER = "lefttrigger"
CONTROLLER_RIGHTTRIGGER = "righttrigger"

CONTROLLER_LEFTXNEG = "leftxneg"
CONTROLLER_LEFTXPOS = "leftxpos"
CONTROLLER_LEFTYNEG = "leftyneg"
CONTROLLER_LEFTYPOS = "leftypos"
CONTROLLER_RIGHTXNEG = "rightxneg"
CONTROLLER_RIGHTXPOS = "rightxpos"
CONTROLLER_RIGHTYNEG = "rightyneg"
CONTROLLER_RIGHTYPOS = "rightypos"


# CONTROLLER_DPAD_UP = CONTROLLER_DPUP
# CONTROLLER_DPAD_DOWN = CONTROLLER_DPDOWN
# CONTROLLER_DPAD_LEFT = CONTROLLER_DPLEFT
# CONTROLLER_DPAD_RIGHT = CONTROLLER_DPRIGHT


class Controller:
    A = "a"
    B = "b"
    X = "x"
    Y = "y"
    START = "start"
    GUIDE = "guide"
    BACK = "back"
    DPUP = "dpup"
    DPLEFT = "dpleft"
    DPRIGHT = "dpright"
    DPDOWN = "dpdown"
    LEFTSHOULDER = "leftshoulder"
    RIGHTSHOULDER = "rightshoulder"
    LEFTSTICK = "leftstick"
    RIGHTSTICK = "rightstick"
    LEFTX = "leftx"
    LEFTY = "lefty"
    RIGHTX = "rightx"
    RIGHTY = "righty"
    LEFTTRIGGER = "lefttrigger"
    RIGHTTRIGGER = "righttrigger"
    LEFTXNEG = "leftxneg"
    LEFTXPOS = "leftxpos"
    LEFTYNEG = "leftyneg"
    LEFTYPOS = "leftypos"
    RIGHTXNEG = "rightxneg"
    RIGHTXPOS = "rightxpos"
    RIGHTYNEG = "rightyneg"
    RIGHTYPOS = "rightypos"


class Key:
    ZERO = "0"
    ONE = "1"
    TWO = "2"
    THREE = "3"
    FOUR = "4"
    FIVE = "5"
    SIX = "6"
    SEVEN = "7"
    EIGHT = "8"
    NINE = "9"
    A = "a"
    AC_BACK = "ac_back"
    AC_BOOKMARKS = "ac_bookmarks"
    AC_FORWARD = "ac_forward"
    AC_HOME = "ac_home"
    AC_REFRESH = "ac_refresh"
    AC_SEARCH = "ac_search"
    AC_STOP = "ac_stop"
    AGAIN = "again"
    ALTERASE = "alterase"
    APOSTROPHE = "apostrophe"
    APPLICATION = "application"
    AUDIOMUTE = "audiomute"
    AUDIONEXT = "audionext"
    AUDIOPLAY = "audioplay"
    AUDIOPREV = "audioprev"
    AUDIOSTOP = "audiostop"
    B = "b"
    BACKSLASH = "backslash"
    BACKSLASH = "backslash"
    BACKSPACE = "backspace"
    BRIGHTNESSDOWN = "brightnessdown"
    BRIGHTNESSUP = "brightnessup"
    C = "c"
    CALCULATOR = "calculator"
    CANCEL = "cancel"
    CAPSLOCK = "capslock"
    CLEAR = "clear"
    CLEARAGAIN = "clearagain"
    COMMA = "comma"
    COMPUTER = "computer"
    COPY = "copy"
    CRSEL = "crsel"
    CURRENCYSUBUNIT = "currencysubunit"
    CURRENCYUNIT = "currencyunit"
    CUT = "cut"
    D = "d"
    DECIMALSEPARATOR = "decimalseparator"
    DELETE = "delete"
    DISPLAYSWITCH = "displayswitch"
    DOWN = "down"
    E = "e"
    EJECT = "eject"
    END = "end"
    EQUALS = "equals"
    ESCAPE = "escape"
    EXECUTE = "execute"
    EXSEL = "exsel"
    F = "f"
    F1 = "f1"
    F10 = "f10"
    F11 = "f11"
    F12 = "f12"
    F13 = "f13"
    F14 = "f14"
    F15 = "f15"
    F16 = "f16"
    F17 = "f17"
    F18 = "f18"
    F19 = "f19"
    F2 = "f2"
    F20 = "f20"
    F21 = "f21"
    F22 = "f22"
    F23 = "f23"
    F24 = "f24"
    F3 = "f3"
    F4 = "f4"
    F5 = "f5"
    F6 = "f6"
    F7 = "f7"
    F8 = "f8"
    F9 = "f9"
    FIND = "find"
    G = "g"
    GRAVE = "grave"
    H = "h"
    HELP = "help"
    HOME = "home"
    I = "i"
    INSERT = "insert"
    INTERNATIONAL1 = "international1"
    INTERNATIONAL2 = "international2"
    INTERNATIONAL3 = "international3"
    INTERNATIONAL4 = "international4"
    INTERNATIONAL5 = "international5"
    INTERNATIONAL6 = "international6"
    INTERNATIONAL7 = "international7"
    INTERNATIONAL8 = "international8"
    INTERNATIONAL9 = "international9"
    J = "j"
    K = "k"
    KBDILLUMDOWN = "kbdillumdown"
    KBDILLUMTOGGLE = "kbdillumtoggle"
    KBDILLUMUP = "kbdillumup"
    KP_0 = "kp_0"
    KP_00 = "kp_00"
    KP_000 = "kp_000"
    KP_1 = "kp_1"
    KP_2 = "kp_2"
    KP_3 = "kp_3"
    KP_4 = "kp_4"
    KP_5 = "kp_5"
    KP_6 = "kp_6"
    KP_7 = "kp_7"
    KP_8 = "kp_8"
    KP_9 = "kp_9"
    KP_A = "kp_a"
    KP_AMPERSAND = "kp_ampersand"
    KP_AT = "kp_at"
    KP_B = "kp_b"
    KP_BACKSPACE = "kp_backspace"
    KP_BINARY = "kp_binary"
    KP_C = "kp_c"
    KP_CLEAR = "kp_clear"
    KP_CLEARENTRY = "kp_clearentry"
    KP_COLON = "kp_colon"
    KP_COMMA = "kp_comma"
    KP_D = "kp_d"
    KP_DBLAMPERSAND = "kp_dblampersand"
    KP_DBLVERTICALBAR = "kp_dblverticalbar"
    KP_DECIMAL = "kp_decimal"
    KP_DIVIDE = "kp_divide"
    KP_E = "kp_e"
    KP_ENTER = "kp_enter"
    KP_EQUALS = "kp_equals"
    KP_EQUALSAS400 = "kp_equalsas400"
    KP_EXCLAM = "kp_exclam"
    KP_F = "kp_f"
    KP_GREATER = "kp_greater"
    KP_HASH = "kp_hash"
    KP_HEXADECIMAL = "kp_hexadecimal"
    KP_LEFTBRACE = "kp_leftbrace"
    KP_LEFTPAREN = "kp_leftparen"
    KP_LESS = "kp_less"
    KP_MEMADD = "kp_memadd"
    KP_MEMCLEAR = "kp_memclear"
    KP_MEMDIVIDE = "kp_memdivide"
    KP_MEMMULTIPLY = "kp_memmultiply"
    KP_MEMRECALL = "kp_memrecall"
    KP_MEMSTORE = "kp_memstore"
    KP_MEMSUBTRACT = "kp_memsubtract"
    KP_MINUS = "kp_minus"
    KP_MULTIPLY = "kp_multiply"
    KP_OCTAL = "kp_octal"
    KP_PERCENT = "kp_percent"
    KP_PERIOD = "kp_period"
    KP_PLUS = "kp_plus"
    KP_PLUSMINUS = "kp_plusminus"
    KP_POWER = "kp_power"
    KP_RIGHTBRACE = "kp_rightbrace"
    KP_RIGHTPAREN = "kp_rightparen"
    KP_SPACE = "kp_space"
    KP_TAB = "kp_tab"
    KP_VERTICALBAR = "kp_verticalbar"
    KP_XOR = "kp_xor"
    L = "l"
    LALT = "lalt"
    LANG1 = "lang1"
    LANG2 = "lang2"
    LANG3 = "lang3"
    LANG4 = "lang4"
    LANG5 = "lang5"
    LANG6 = "lang6"
    LANG7 = "lang7"
    LANG8 = "lang8"
    LANG9 = "lang9"
    LCTRL = "lctrl"
    LEFT = "left"
    LEFTBRACKET = "leftbracket"
    LGUI = "lgui"
    LOCKINGCAPSLOCK = "lockingcapslock"
    LOCKINGNUMLOCK = "lockingnumlock"
    LOCKINGSCROLLLOCK = "lockingscrolllock"
    LSHIFT = "lshift"
    M = "m"
    MAIL = "mail"
    MEDIASELECT = "mediaselect"
    MENU = "menu"
    MINUS = "minus"
    MODE = "mode"
    MUTE = "mute"
    N = "n"
    NONUSBACKSLASH = "nonusbackslash"
    NONUSHASH = "nonushash"
    NUMLOCKCLEAR = "numlockclear"
    O = "o"
    OPER = "oper"
    OUT = "out"
    P = "p"
    PAGEDOWN = "pagedown"
    PAGEUP = "pageup"
    PASTE = "paste"
    PAUSE = "pause"
    PERIOD = "period"
    POWER = "power"
    PRINTSCREEN = "printscreen"
    PRIOR = "prior"
    Q = "q"
    R = "r"
    RALT = "ralt"
    RCTRL = "rctrl"
    RETURN = "return"
    RETURN2 = "return2"
    RGUI = "rgui"
    RIGHT = "right"
    RIGHTBRACKET = "rightbracket"
    RSHIFT = "rshift"
    S = "s"
    SCROLLLOCK = "scrolllock"
    SELECT = "select"
    SEMICOLON = "semicolon"
    SEPARATOR = "separator"
    SLASH = "slash"
    SLEEP = "sleep"
    SPACE = "space"
    STOP = "stop"
    SYSREQ = "sysreq"
    T = "t"
    TAB = "tab"
    THOUSANDSSEPARATOR = "thousandsseparator"
    U = "u"
    UNDO = "undo"
    UNKNOWN = "unknown"
    UP = "up"
    V = "v"
    VOLUMEDOWN = "volumedown"
    VOLUMEUP = "volumeup"
    W = "w"
    WWW = "www"
    X = "x"
    Y = "y"
    Z = "z"


# def nes_controller_keyboard_mapping(port_index):
#     mapping = {
#         Key.X: NES_GAMEPAD_A,
#         Key.C: NES_GAMEPAD_B,
#         Key.LEFT: NES_GAMEPAD_LEFT,
#         Key.RIGHT: NES_GAMEPAD_RIGHT,
#         Key.UP: NES_GAMEPAD_UP,
#         Key.DOWN: NES_GAMEPAD_DOWN,
#         Key.RETURN: NES_GAMEPAD_START,
#         Key.SPACE: NES_GAMEPAD_SELECT,
#     }
#     return mapping


# def nes_controller_gamepad_mapping(port_index):
#     mapping = {
#         Controller.A: NES_GAMEPAD_B,
#         Controller.B: NES_GAMEPAD_A,
#         Controller.X: NES_GAMEPAD_A,
#         Controller.Y: NES_GAMEPAD_B,
#         Controller.DPLEFT: NES_GAMEPAD_LEFT,
#         Controller.DPRIGHT: NES_GAMEPAD_RIGHT,
#         Controller.DPUP: NES_GAMEPAD_UP,
#         Controller.DPDOWN: NES_GAMEPAD_DOWN,
#         Controller.LEFTXNEG: NES_GAMEPAD_LEFT,
#         Controller.LEFTXPOS: NES_GAMEPAD_RIGHT,
#         Controller.LEFTYNEG: NES_GAMEPAD_UP,
#         Controller.LEFTYPOS: NES_GAMEPAD_DOWN,
#         Controller.START: NES_GAMEPAD_START,
#         Controller.BACK: NES_GAMEPAD_SELECT,
#     }
#     return mapping


# def retroarch_remap_name(input_event):
#     # FIXME: rename input_event to something else...
#     # sdl_controller_event? sdl_controller_input?
#     mapping = {
#         Controller.A: "btn_a",
#         Controller.B: "btn_b",
#         Controller.X: "btn_x",
#         Controller.Y: "btn_y",
#         Controller.START: "btn_start",
#         Controller.GUIDE: "",
#         Controller.BACK: "btn_select",
#         Controller.DPUP: "btn_up",
#         Controller.DPLEFT: "btn_left",
#         Controller.DPRIGHT: "btn_right",
#         Controller.DPDOWN: "btn_down",
#         Controller.LEFTSHOULDER: "btn_l",
#         Controller.RIGHTSHOULDER: "btn_r",
#         Controller.LEFTSTICK: "btn_l3",
#         Controller.RIGHTSTICK: "btn_r3",
#         Controller.LEFTTRIGGER: "btn_l2",
#         Controller.RIGHTTRIGGER: "btn_r2",
#         Controller.LEFTXNEG: "stk_l_x-",
#         Controller.LEFTXPOS: "stk_l_x+",
#         Controller.LEFTYNEG: "stk_l_y-",
#         Controller.LEFTYPOS: "stk_l_y+",
#         Controller.RIGHTXNEG: "stk_r_x-",
#         Controller.RIGHTXPOS: "stk_r_x+",
#         Controller.RIGHTYNEG: "stk_r_y-",
#         Controller.RIGHTYPOS: "stk_r_y+",
#         # CONTROLLER_LEFTX: "",
#         # CONTROLLER_LEFTY: "",
#         # CONTROLLER_RIGHTX: "",
#         # CONTROLLER_RIGHTY: "",
#     }
#     return mapping[input_event]


# def retroarch_remap_name_for_port(input_event, port_index):
#     return "input_player{}_{}".format(
#         port_index + 1, retroarch_remap_name(input_event)
#     )
#
#
# if __name__ == "__main__":
#     nes = nes_controller_gamepad_mapping(0)
#     nestopia = nestopia_retropad_mapping_for_port(0)
#     for controller_input, nes_action in nes.items():
#         for remap_id, nes_action_2 in nestopia.items():
#             if nes_action_2 == nes_action:
#                 remap_name = retroarch_remap_name_for_port(controller_input, 0)
#                 print(remap_name, remap_id)
