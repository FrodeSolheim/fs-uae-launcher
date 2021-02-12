import hashlib
import os

from fsbc import settings
from fsgamesys.drivers.mednafendriver import MednafenDriver
from fsgamesys.drivers.mess.messsmsdriver import MessSmsDriver
from fsgamesys.options.option import Option
from fsgamesys.platforms.platform import Platform
from fsgamesys.platforms.loader import SimpleLoader

"""
FIXME: Some PAL games are 256x240, e.g. Fantastic Dizzy
"""


class MasterSystemPlatform(Platform):
    PLATFORM_NAME = "Master System"

    def driver(self, fsgc):
        if settings.get(Option.SMS_DRIVER) == "mess":
            return MessSmsDriver(fsgc)
        else:
            return MasterSystemMednafenFSDriver(fsgc)

    def loader(self, fsgc):
        return MasterSystemLoader(fsgc)


class MasterSystemLoader(SimpleLoader):
    pass


class MasterSystemMednafenDriver(MednafenDriver):
    CONTROLLER = {
        "type": "gamepad",
        "description": "Gamepad",
        "mapping_name": "mastersystem",
    }

    PORTS = [
        {"description": "1st Controller", "types": [CONTROLLER]},
        {"description": "2nd Controller", "types": [CONTROLLER]},
    ]

    def __init__(self, fsgc, vanilla=True):
        super().__init__(fsgc, vanilla)
        self.helper = MasterSystemHelper(self.options)
        # FIXME: Not checked
        self.save_handler.set_save_data_is_emulator_specific(True)
        # self.save_handler.set_srm_alias(".sav")

    def prepare(self):
        print("[SMS] Mednafen driver preparing...")
        super().prepare()
        rom_path = self.helper.prepare_rom(self)
        # self.helper.read_rom_metadata(rom_path)
        # self.init_mega_drive_model()
        # for i in range(len(self.PORTS)):
        #     self.init_mega_drive_port(i)
        # self.init_mednafen_crop_from_viewport()
        self.set_mednafen_aspect(4, 3)

        # We do aspect calculation separately. Must not be done twice.
        # FIXME: Option does not exist, check that end result is correct!
        # self.emulator.args.extend(["-sms.correct_aspect", "0"])

        # ROM path must be added at the end of the argument list
        self.emulator.args.append(rom_path)

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

    # def game_video_par(self):
    #     size = self.game_video_size()
    #     return (4 / 3) / (size[0] / size[1])

    def game_video_size(self):
        if self.is_pal():
            size = (256, 240)
        else:
            size = (256, 192)
        return size

    def get_game_file(self, config_key="cartridge_slot"):
        return None


class MasterSystemMednafenFSDriver(MasterSystemMednafenDriver):
    def __init__(self, fsgs):
        super().__init__(fsgs, vanilla=False)


class MasterSystemHelper:
    def __init__(self, options):
        self.options = options

    # def model(self):
    #     if self.options[Option.SMD_MODEL] == SMD_MODEL_NTSC:
    #         return SMD_MODEL_NTSC
    #     if self.options[Option.SMD_MODEL] == SMD_MODEL_NTSC_J:
    #         return SMD_MODEL_NTSC_J
    #     if self.options[Option.SMD_MODEL] == SMD_MODEL_PAL:
    #         return SMD_MODEL_PAL
    #     # FIXME: REMOVE?
    #     # return SMD_MODEL_AUTO
    #     return SMD_MODEL_NTSC

    # def set_model_name_from_model(self, driver):
    #     model = self.model()
    #     if model == SMD_MODEL_NTSC:
    #         driver.set_model_name("Genesis")
    #     elif model == SMD_MODEL_PAL:
    #         driver.set_model_name("Mega Drive PAL")
    #     elif model == SMD_MODEL_NTSC_J:
    #         driver.set_model_name("Mega Drive NTSC-J")

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
