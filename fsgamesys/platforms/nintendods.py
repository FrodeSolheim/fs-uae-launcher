import os

from fsbc import settings
from fsgamesys.drivers.gamedriver import Emulator, GameDriver
from fsgamesys.knownfiles import KnownFile
from fsgamesys.options.option import Option
from fsgamesys.platforms.loader import SimpleLoader
from fsgamesys.platforms.platform import Platform

NDS_PLATFORM_NAME = "Nintendo DS"
NDS_CONTROLLER = {
    "type": "gamepad",
    "description": "Gamepad",
    "mapping_name": "ngc",
}


class NintendoDSPlatform(Platform):
    PLATFORM_NAME = NDS_PLATFORM_NAME

    def driver(self, fsgc):
        driver = settings.get(Option.NDS_EMULATOR)
        if driver == "desmume":
            return DesmumeDriver(fsgc)
        return MelonDSDriver(fsgc)

    def loader(self, fsgc):
        return NintendoDSLoader(fsgc)


class NintendoDSLoader(SimpleLoader):
    pass


class DesmumeDriver(GameDriver):
    PORTS = [{"description": "Controller 1", "types": [NDS_CONTROLLER]}]

    def __init__(self, fsgc):
        super().__init__(fsgc)
        self.helper = NintendoDSHelper(self.options)
        self.emulator = Emulator(
            "desmume", path=self.options[Option.DESMUME_PATH]
        )
        self.emulator.allow_home_access = True

    def prepare(self):
        rom_path = self.get_game_file()
        self.emulator.args.append(rom_path)

    def finish(self):
        pass


NDS_PLATFORM_ID = "nds"
NDS_BIOS7_BIN = KnownFile(
    "24f67bdea115a2c847c8813a262502ee1607b7df", NDS_PLATFORM_ID, "bios7.bin"
)
NDS_BIOS9_BIN = KnownFile(
    "bfaac75f101c135e32e2aaf541de6b1be4c8c62d", NDS_PLATFORM_ID, "bios9.bin"
)
NDS_FIRMWARE_BIN = KnownFile(
    "ae22de59fbf3f35ccfbeacaeba6fa87ac5e7b14b", NDS_PLATFORM_ID, "firmware.bin"
)


class MelonDSDriver(GameDriver):
    PORTS = [{"description": "Controller 1", "types": [NDS_CONTROLLER]}]

    def __init__(self, fsgc):
        super().__init__(fsgc)
        self.helper = NintendoDSHelper(self.options)
        self.emulator = Emulator(
            "melonDS", path=self.options[Option.MELONDS_PATH]
        )
        self.emulator.allow_home_access = True

        os.path.join(self.cwd.path, "bios7.bin")
        os.path.join(self.cwd.path, "bios9.bin")
        os.path.join(self.cwd.path, "firmware.bin")

    def prepare(self):
        rom_path = self.get_game_file()
        self.emulator.args.append(rom_path)
        self.prepare_bios(NDS_BIOS7_BIN, "bios7.bin")
        self.prepare_bios(NDS_BIOS9_BIN, "bios9.bin")
        self.prepare_bios(NDS_FIRMWARE_BIN, "firmware.bin")

    def prepare_bios(self, known_file, name):
        bios_path = os.path.join(self.cwd.path, name)
        if not os.path.exists(os.path.dirname(bios_path)):
            os.makedirs(os.path.dirname(bios_path))
        src = self.fsgc.file.find_by_sha1(known_file.sha1)
        if not src:
            raise Exception(
                "Could not find {} (SHA-1: {}".format(
                    known_file.name, known_file.sha1
                )
            )
        self.fsgc.file.copy_game_file(src, bios_path)

    def finish(self):
        pass


class NintendoDSHelper:
    def __init__(self, options):
        self.options = options
