import os

from fsgs.drivers.dolphindriver import DolphinDriver, DolphinInputMapper
from fsgs.drivers.gamedriver import GameDriver, Emulator
from fsgs.platform import Platform
from fsgs.platforms.loader import SimpleLoader

NDS_PLATFORM_NAME = "Nintendo DS"
NDS_CONTROLLER = {
    "type": "gamepad",
    "description": "Gamepad",
    "mapping_name": "ngc",
}


class NintendoDSPlatform(Platform):
    PLATFORM_NAME = NDS_PLATFORM_NAME

    def driver(self, fsgc):
        return NintendoDSDriver(fsgc)

    def loader(self, fsgc):
        return NintendoDSLoader(fsgc)


class NintendoDSLoader(SimpleLoader):
    pass


class NintendoDSDriver(GameDriver):
    PORTS = [{"description": "Controller 1", "types": [NDS_CONTROLLER]}]

    def __init__(self, fsgc):
        super().__init__(fsgc)
        self.helper = NintendoDSHelper(self.options)
        self.emulator = Emulator("desmume")
        self.emulator.allow_system_emulator = True

    def prepare(self):
        rom_path = self.get_game_file()
        self.emulator.args.append(rom_path)

    def finish(self):
        pass


class NintendoDSHelper:
    def __init__(self, options):
        self.options = options
