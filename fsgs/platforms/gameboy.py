import hashlib
import os

from fsgs import Option
from fsgs.drivers.mednafendriver import MednafenDriver
from fsgs.platform import Platform
from fsgs.platforms.loader import SimpleLoader


class GameBoyPlatform(Platform):
    PLATFORM_NAME = "Game Boy"

    def driver(self, fsgc):
        return MednafenGbDriver(fsgc)

    def loader(self, fsgc):
        return GameBoyLoader(fsgc)


class GameBoyLoader(SimpleLoader):
    pass


class MednafenGbDriver(MednafenDriver):
    CONTROLLER = {
        "type": "gamepad",
        "description": "Built-in Controller",
        "mapping_name": "gameboy",
    }

    PORTS = [
        {
            "description": "Controller",
            "types": [CONTROLLER]
        },
    ]

    def __init__(self, fsgc):
        super().__init__(fsgc)
        self.helper = GameBoyHelper(self.options)

    def prepare(self):
        super().prepare()
        rom_path = self.helper.prepare_rom(self)
        self.emulator.args.append(rom_path)

    def get_game_refresh_rate(self):
        return 59.73

    def mednafen_input_mapping(self, port):
        return {
            "A": "gb.input.builtin.gamepad.a",
            "B": "gb.input.builtin.gamepad.b",
            "UP": "gb.input.builtin.gamepad.up",
            "DOWN": "gb.input.builtin.gamepad.down",
            "LEFT": "gb.input.builtin.gamepad.left",
            "RIGHT": "gb.input.builtin.gamepad.right",
            "SELECT": "gb.input.builtin.gamepad.select",
            "START": "gb.input.builtin.gamepad.start",
        }

    def mednafen_rom_extensions(self):
        return [".gb"]

    def mednafen_scanlines_setting(self):
        return 0

    def mednafen_special_filter(self):
        return "nn2x"

    def mednafen_system_prefix(self):
        return "gb"

    def game_video_par(self):
        # return (4.7 / 4.3) / (160 / 144)
        # Close enough to 1.0, might just as well go with that.
        return 1.0

    def game_video_size(self):
        return 160, 144

    def get_game_file(self, config_key="cartridge_slot"):
        return None


class GameBoyHelper:
    def __init__(self, options):
        self.options = options

    def prepare_rom(self, driver):
        file_uri = self.options[Option.CARTRIDGE_SLOT]
        input_stream = driver.fsgc.file.open(file_uri)
        _, ext = os.path.splitext(file_uri)
        return self.prepare_rom_with_stream(driver, input_stream, ext)

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
            os.path.dirname(path), sha1_obj.hexdigest()[:8].upper() + ext)
        os.rename(path, new_path)
        return new_path
