import hashlib
import os
from binascii import unhexlify

from fsbc import settings
from fsgs.drivers.gamedriver import Emulator, GameDriver
from fsgs.drivers.mednafendriver import MednafenDriver
from fsgs.drivers.mess.messnesdriver import MessNesDriver
from fsgs.drivers.retroarchdriver import RetroArchDriver
from fsgs.option import Option
from fsgs.platform import Platform
from fsgs.platforms.loader import SimpleLoader

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

    def driver(self, fsgc):
        # if settings.get(Option.NES_DRIVER) == "mess":
        #     return MessNesDriver(fsgc)
        # else:
        #     return NintendoMednafenDriver(fsgc)
        driver = settings.get(Option.NES_EMULATOR)

        # FIXME: nestopia-libretro? retroarch-nestopia?
        if driver in ["retroarch-nestopia", "libretro-nestopia"]:
            return NintendoRetroArchDriver(fsgc)
        elif driver in ["mame", "mess"]:
            return MessNesDriver(fsgc)
        elif driver == "higan":
            return NintendoHiganDriver(fsgc)
        return NintendoMednafenDriver(fsgc)

    def loader(self, fsgc):
        return NintendoLoader(fsgc)


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


class NintendoMednafenDriver(MednafenDriver):
    PORTS = NES_PORTS

    def __init__(self, fsgs):
        super().__init__(fsgs)
        self.helper = NintendoHelper(self.options)
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

        if self.helper.model() == NES_MODEL_PAL:
            self.set_model_name("Nintendo (PAL)")
            self.emulator.args.extend(["-{}.pal".format(pfx), "1"])
        else:
            if self.helper.model() == NES_MODEL_FAMICOM:
                self.set_model_name("Famicom")
            else:
                self.set_model_name("Nintendo (NTSC)")
            self.emulator.args.extend(["-{}.pal".format(pfx), "0"])
        self.emulator.args.extend(["-{}.fnscan".format(pfx), "0"])

        self.emulator.env["FSGS_ASPECT"] = "4/3"

        viewport = self.options[Option.VIEWPORT]
        if viewport == "0 0 256 240 = 0 0 256 240":
            self.emulator.env["FSGS_CROP"] = "0,0,256,240"
        # elif viewport == "0 0 256 240 = 0 8 256 224":
        #     self.emulator.env["FSGS_CROP"] = "0,8,256,224"
        elif viewport == "0 0 256 240 = 8 0 240 240":
            self.emulator.env["FSGS_CROP"] = "8,0,240,240"
        elif viewport == "0 0 256 240 = 8 8 240 224":
            self.emulator.env["FSGS_CROP"] = "8,8,240,224"
        else:
            self.emulator.env["FSGS_CROP"] = "0,8,256,224"

        self.emulator.args.append(self.helper.prepare_rom(self))

    def finish(self):
        print("[DRIVER] Mednafen NES Driver finishing...")
        super().finish()

    # def mednafen_extra_graphics_options(self):
    #     options = []
    #     if self.nes_clip_sides():
    #         options.extend(["-nes.clipsides", "1"])
    #     return options

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
        # FIXME
        if self.is_pal():
            size = (256, 240)
        else:
            size = (256, 224)
        # if self.nes_clip_sides():
        #     size = (size[0] - 16, size[1])
        return size

    # def nes_clip_sides(self):
    #     # FIXME: Sane default? -Or enable this in a per-game config
    #     # instead? SMB3 looks better with this
    #     # return True
    #     return False

    def get_game_file(self, config_key="cartridge_slot"):
        # path = super().get_game_file()
        #
        # # FIXME: Replace and do in one go without going via super
        # input_stream = self.fsgc.file.open(path)
        # _, ext = os.path.splitext(path)
        # return self.prepare_rom_with_stream(self, input_stream, ext)
        # return self.helper.prepare_rom(self)
        return None


class NintendoRetroArchDriver(RetroArchDriver):
    PORTS = NES_PORTS

    def __init__(self, fsgc):
        super().__init__(fsgc, "nestopia_libretro", "RetroArch/Nestopia")
        self.helper = NintendoHelper(self.options)

    def prepare(self):
        super().prepare()
        with self.open_retroarch_core_options() as f:
            if self.helper.model() == NES_MODEL_PAL:
                self.set_model_name("Nintendo (PAL)")
                f.write("nestopia_favored_system = pal\n")
            elif self.helper.model() == NES_MODEL_FAMICOM:
                self.set_model_name("Famicom")
                f.write("nestopia_favored_system = famicom\n")
            else:
                self.set_model_name("Nintendo (NTSC)")
                f.write("nestopia_favored_system = ntsc\n")

            viewport = self.options[Option.VIEWPORT]
            if viewport == "0 0 256 240 = 0 0 256 240":
                overscan_h, overscan_v = "disabled", "disabled"
            # elif viewport == "0 0 256 240 = 0 8 256 224":
            #     return 256, 224
            elif viewport == "0 0 256 240 = 8 0 240 240":
                overscan_h, overscan_v = "enabled", "disabled"
            elif viewport == "0 0 256 240 = 8 8 240 224":
                overscan_h, overscan_v = "enabled", "enabled"
            else:
                overscan_h, overscan_v = "disabled", "enabled"
            f.write("nestopia_overscan_h = {}\n".format(overscan_h))
            f.write("nestopia_overscan_v = {}\n".format(overscan_v))
        self.emulator.args.append(self.helper.prepare_rom(self))

    def game_video_size(self):
        # FIXME: Account for horizontal overscan
        # FIXME: Account for vertical overscan

        viewport = self.options[Option.VIEWPORT]
        if viewport == "0 0 256 240 = 0 0 256 240":
            return 256, 240
        # elif viewport == "0 0 256 240 = 0 8 256 224":
        #     return 256, 224
        elif viewport == "0 0 256 240 = 8 0 240 240":
            return 240, 240
        elif viewport == "0 0 256 240 = 8 8 240 224":
            return 240, 224
        else:
            return 256, 224

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


class NintendoHiganDriver(GameDriver):
    PORTS = NES_PORTS

    def __init__(self, fsgs):
        super().__init__(fsgs)
        self.emulator = Emulator("higan")
        self.emulator.allow_system_emulator = True
        self.helper = NintendoHelper(self.options)

    def prepare(self):
        if self.use_fullscreen():
            self.emulator.args.append("--fullscreen")

        # model = self.helper.nes_model()

        rom_path = self.get_game_file()
        self.helper.fix_ines_rom(rom_path)
        self.emulator.args.extend([rom_path])


class NintendoHelper:
    def __init__(self, options):
        self.options = options

    def model(self):
        model = self.options[Option.NES_MODEL]
        if model in ["", NES_MODEL_NTSC]:
            return NES_MODEL_NTSC
        elif model == NES_MODEL_PAL:
            return NES_MODEL_PAL
        elif model == NES_MODEL_FAMICOM:
            return NES_MODEL_FAMICOM
        else:
            print("[NES] Warning: Invalid model:", model)
            return NES_MODEL_NTSC

    def pal(self):
        return self.model() == NES_MODEL_PAL

    def fix_ines_rom(self, path):
        data1 = b""
        with open(path, "rb") as f:
            # Start iNES Hack -------------------------------------------------
            data = f.read(16)
            if len(data) == 16 and data.startswith(b"NES\x1a"):
                print("[DRIVER] Stripping iNES header")
            else:
                # No iNES header, include data
                data1 = data
            # End iNES Hack ---------------------------------------------------
            data2 = f.read()
        with open(path, "wb") as f:
            ines_header = self.options[Option.NES_INES_HEADER]
            if ines_header:
                assert len(ines_header) == 32
                f.write(unhexlify(ines_header))
            f.write(data1)
            f.write(data2)
        return path

    def prepare_rom(self, driver):
        file_uri = self.options[Option.CARTRIDGE_SLOT]
        input_stream = driver.fsgc.file.open(file_uri)
        _, ext = os.path.splitext(file_uri)
        return self.prepare_rom_with_stream(driver, input_stream, ext)

    def prepare_rom_with_stream(self, driver, input_stream, ext):
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
            header = self.options[Option.NES_INES_HEADER]
            if header:
                assert len(header) == 16 * 2
                f.write(unhexlify(header))
                sha1_obj.update(unhexlify(header))
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
