import hashlib
import os
from binascii import hexlify

from fsbc import settings
from fsgs.drivers.mednafendriver import MednafenDriver
from fsgs.drivers.messdriver import MessDriver
from fsgs.drivers.retroarchdriver import RetroArchDriver
from fsgs.option import Option
from fsgs.platform import Platform
from fsgs.platforms.loader import SimpleLoader

SMD_MODEL_NTSC = "ntsc"
SMD_MODEL_NTSC_J = "ntsc-j"
SMD_MODEL_PAL = "pal"
SMD_CONTROLLER_TYPE = "gamepad"
SMD_CONTROLLER = {
    "type": SMD_CONTROLLER_TYPE,
    "description": "Gamepad",
    "mapping_name": "megadrive",
}
SMD_6BUTTON_CONTROLLER_TYPE = "gamepad6"
SMD_6BUTTON_CONTROLLER = {
    "type": SMD_6BUTTON_CONTROLLER_TYPE,
    "description": "Gamepad",
    "mapping_name": "megadrive",
}
NO_CONTROLLER_TYPE = "none"
NO_CONTROLLER = {
    "type": NO_CONTROLLER_TYPE,
    "description": "None",
    "mapping_name": "",
}
SMD_PORTS = [
    {
        "description": "Port 1",
        "types": [SMD_CONTROLLER, SMD_6BUTTON_CONTROLLER, NO_CONTROLLER],
        "type_option": "smd_port_1_type",
        "device_option": "smd_port_1",
    },
    {
        "description": "Port 2",
        "types": [SMD_CONTROLLER, SMD_6BUTTON_CONTROLLER, NO_CONTROLLER],
        "type_option": "smd_port_2_type",
        "device_option": "smd_port_2",
    },
]


class MegaDrivePlatform(Platform):
    PLATFORM_NAME = "Mega Drive"

    def driver(self, fsgc):
        emulator = settings.get(Option.SMD_EMULATOR)

        if emulator in ["retroarch-fs", "retroarch-fs/genesisplusgx"]:
            return MegaDriveRetroArchDriver(fsgc)
        if emulator in ["mame-fs"]:
            return MegaDriveMameDriver(fsgc)
        if emulator in ["mednafen"]:
            return MegaDriveMednafenDriver(fsgc)

        # FIXME: Vanilla retroarch not supported yet
        if emulator in ["retroarch", "retroarch/genesisplusgx"]:
            return MegaDriveRetroArchDriver(fsgc)
        # Deprecated name
        if emulator in ["retroarch-genesis-plus-gx"]:
            return MegaDriveRetroArchDriver(fsgc)
        # Legacy names
        if emulator in ["mame", "mess"]:
            return MegaDriveMameDriver(fsgc)

        return MegaDriveMednafenFSDriver(fsgc)

    def loader(self, fsgc):
        return MegaDriveLoader(fsgc)


class MegaDriveLoader(SimpleLoader):
    def load(self, values):
        super().load(values)
        self.config[Option.SMD_MODEL] = values["smd_model"]
        self.config[Option.SMD_PORT_1_TYPE] = values["smd_port_1_type"]
        self.config[Option.SMD_PORT_2_TYPE] = values["smd_port_2_type"]
        # self.config[Option.SMD_PORT_3_TYPE] = values["smd_port_3_type"]
        # self.config[Option.SMD_PORT_4_TYPE] = values["smd_port_4_type"]

        # FIXME: Should be able to remove this now (smd_model in database)
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


class MegaDriveMameDriver(MessDriver):
    PORTS = SMD_PORTS

    def __init__(self, fsgs):
        super().__init__(fsgs)
        self.helper = MegaDriveHelper(self.options)
        self.save_handler.set_save_data_is_emulator_specific(True)
        self.save_handler.set_mame_driver(self.get_mame_driver())

    def prepare(self):
        print("[SMD] MAME driver preparing...")
        super().prepare()
        self.emulator.args.extend(["-cart", self.helper.prepare_rom(self)])

    def get_mame_driver(self):
        self.helper.set_model_name_from_model(self)
        if self.helper.model() == SMD_MODEL_NTSC:
            return "genesis"
        elif self.helper.model() == SMD_MODEL_PAL:
            return "megadriv"
        elif self.helper.model() == SMD_MODEL_NTSC_J:
            return "megadrij"
        raise Exception("Could not determine SMD MAME driver")

    def get_mess_input_mapping(self, _):
        return {
            "START": "P#_START",
            "MODE": "P#_SELECT",
            "UP": "P#_JOYSTICK_UP",
            "DOWN": "P#_JOYSTICK_DOWN",
            "LEFT": "P#_JOYSTICK_LEFT",
            "RIGHT": "P#_JOYSTICK_RIGHT",
            "A": "P#_BUTTON1",
            "B": "P#_BUTTON2",
            "C": "P#_BUTTON3",
            "X": "P#_BUTTON4",
            "Y": "P#_BUTTON5",
            "Z": "P#_BUTTON6",
        }

    def get_mess_romset(self):
        return self.get_mame_driver(), {}


class MegaDriveMednafenDriver(MednafenDriver):
    PORTS = SMD_PORTS

    def __init__(self, fsgs, vanilla=True):
        super().__init__(fsgs, vanilla)
        self.helper = MegaDriveHelper(self.options)
        self.save_handler.set_save_data_is_emulator_specific(True)
        # self.save_handler.set_srm_alias(".sav")

    def prepare(self):
        print("[SMD] Mednafen driver preparing...")
        super().prepare()
        rom_path = self.helper.prepare_rom(self)
        self.helper.read_rom_metadata(rom_path)
        self.init_mega_drive_model()
        for i in range(len(self.PORTS)):
            self.init_mega_drive_port(i)
        self.init_mednafen_crop_from_viewport()
        self.set_mednafen_aspect(4, 3)
        # We do aspect calculation separately. Must not be done twice.
        self.emulator.args.extend(["-md.correct_aspect", "0"])
        # ROM path must be added at the end of the argument list
        self.emulator.args.append(rom_path)

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

    def init_mega_drive_port(self, i):
        t = self.ports[i].type
        n = i + 1
        if t == SMD_CONTROLLER_TYPE:
            t = "gamepad"
        elif t == SMD_6BUTTON_CONTROLLER_TYPE:
            t = "gamepad6"
        elif t == NO_CONTROLLER_TYPE:
            t = "none"
        else:
            self.logger.warning(
                "Unknown port type '{}' for Mega Drive port {}".format(t, n)
            )
            t = "gamepad"
        self.emulator.args.extend(["-md.input.port{}".format(n), t])

    def init_mednafen_crop_from_viewport(self):
        viewport = self.options[Option.VIEWPORT]
        if viewport:
            if viewport.startswith("0 0 320 240 ="):
                viewport_src, viewport = self.mednafen_viewport()
                self.emulator.env["FSGS_CROP"] = "{},{},{},{}".format(
                    viewport[0], viewport[1], viewport[2], viewport[3]
                )
        else:
            if self.scaling == self.NO_SCALING:
                if self.helper.model() == SMD_MODEL_PAL:
                    self.emulator.env["FSGS_CROP"] = "0,0,320,240"
                else:
                    self.emulator.env["FSGS_CROP"] = "0,8,320,224"

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

    def get_game_file(self, config_key="cartridge_slot"):
        return None


class MegaDriveMednafenFSDriver(MegaDriveMednafenDriver):
    def __init__(self, fsgs):
        super().__init__(fsgs, vanilla=False)


class MegaDriveRetroArchDriver(RetroArchDriver):
    PORTS = SMD_PORTS

    def __init__(self, fsgc):
        super().__init__(
            fsgc, "genesis_plus_gx_libretro", "RetroArch/GenesisPlusGX"
        )
        self.helper = MegaDriveHelper(self.options)
        self.save_handler.set_save_data_is_emulator_specific(True)

    def prepare(self):
        print("[SMD] RetroArch/GenesisPlusGX driver preparing...")
        super().prepare()
        hw = "mega drive / genesis"
        region = self.init_mega_drive_model()
        for i in range(len(self.PORTS)):
            self.init_mega_drive_port(i)
        with self.open_retroarch_core_options() as f:
            f.write('genesis_plus_gx_system_hw = "{}"\n'.format(hw))
            f.write("genesis_plus_gx_region_detect = {}\n".format(region))
        self.emulator.args.append(self.helper.prepare_rom(self))

    def init_mega_drive_model(self):
        self.helper.set_model_name_from_model(self)
        if self.helper.model() == SMD_MODEL_NTSC:
            return "ntsc-u"
        elif self.helper.model() == SMD_MODEL_PAL:
            return "pal"
        elif self.helper.model() == SMD_MODEL_NTSC_J:
            return "ntsc-j"
        return "ntsc-u"

    def init_mega_drive_port(self, i):
        t = self.ports[i].type
        n = i + 1
        if t == SMD_CONTROLLER_TYPE:
            t = "257"
        elif t == SMD_6BUTTON_CONTROLLER_TYPE:
            t = "513"
        elif t == NO_CONTROLLER_TYPE:
            t = "0"
        else:
            self.logger.warning(
                "Unknown port type '{}' for Mega Drive port {}".format(t, n)
            )
            t = "gamepad"
        # FIXME: Note, this only works for p1 and p2. Port 3 and beyond
        # supports RetroPad only?
        self.retroarch_config["input_libretro_device_p{}".format(n)] = t

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

        # FIXME: PAL?
        return 320, 224

    def retroarch_input_mapping(self, port):
        n = port + 1
        return {
            "A": "input_player{}_y".format(n),
            "B": "input_player{}_b".format(n),
            "C": "input_player{}_a".format(n),
            "X": "input_player{}_l".format(n),
            "Y": "input_player{}_x".format(n),
            "Z": "input_player{}_r".format(n),
            "UP": "input_player{}_up".format(n),
            "DOWN": "input_player{}_down".format(n),
            "LEFT": "input_player{}_left".format(n),
            "RIGHT": "input_player{}_right".format(n),
            "MODE": "input_player{}_select".format(n),
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

    def read_rom_metadata(self, rom_path):
        # FIXME: Move to MegaDriveHeaderParser
        # http://md.squee.co/Howto:Initialise_a_Mega_Drive
        # https://en.wikibooks.org/wiki/Genesis_Programming
        with open(rom_path, "rb") as f:
            data = f.read(0x200)
        if not len(data) == 0x200:
            print("[SMD] Did not read 0x200 header bytes")
            return
        region = data[0x200 - 16 :]
        # notes = data[0x200 - 16 - 52]
        sram_end = data[0x200 - 16 - 52 - 4 * 1 : 0x200 - 16 - 52 - 4 * 0]
        sram_start = data[0x200 - 16 - 52 - 4 * 2 : 0x200 - 16 - 52 - 4 * 1]
        sram_type = data[0x200 - 16 - 52 - 4 * 3 : 0x200 - 16 - 52 - 4 * 2]

        sram_end = hexlify(sram_end)
        sram_start = hexlify(sram_start)
        # sram_type = hexlify(sram_type)
        sram_start = int(sram_start, 16)
        sram_end = int(sram_end, 16)
        print("[SMD] Region:", repr(region))
        print("[SMD] SRAM Type :", repr(sram_type))
        if sram_type[0] == 0x52:
            print(" - 0x52 OK")
        else:
            print(" - 0x52 MISSING")
        if sram_type[1] == 0x41:
            print(" - 0x41 OK")
        else:
            print(" - 0x41 MISSING")
        is_backup = (sram_type[2] & 0b01000000) != 0
        odd, even = False, False
        if (sram_type[2] & 0b00011000) == 0b00011000:
            odd = True
        elif (sram_type[2] & 0b00011000) == 0b00010000:
            even = True
        elif (sram_type[2] & 0b00011000) == 0b00000000:
            even = True
            odd = True
        print(" - Is backup RAM?", is_backup)
        print(" - Odd?", odd, "Even?", even)
        print("[SMD] SRAM Start:", repr(sram_start))
        print("[SMD] SRAM End  :", repr(sram_end))

    # FIXME: Shared, move into common module (find all occurrences)
    def prepare_rom(self, driver):
        file_uri = self.options[Option.CARTRIDGE_SLOT]
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


class MegaDriveHeaderParser:
    def __init__(self):
        self.sram = False
        self.sram_start = 0
        self.sram_end = 0
        self.sram_size = 0
        self.sram_odd_only = False
        self.sram_even_only = False
        self.sram_odd_and_even = False

    def parse_file(self, path):
        with open(path, "rb") as f:
            data = f.read(0x200)
        if not len(data) == 0x200:
            return False
        return self.parse_data(data)

    def parse_data(self, data):
        if not len(data) >= 0x200:
            return False
