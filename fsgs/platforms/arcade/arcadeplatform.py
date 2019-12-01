from fsbc import settings
from fsgs.option import Option
from fsgs.platform import Platform
from fsgs.platforms.arcade.mamearcadedriver import MameArcadeDriver
from fsgs.platforms.loader import SimpleLoader


class ArcadePlatformHandler(Platform):
    PLATFORM_NAME = "Arcade"

    def driver(self, fsgc):
        driver = settings.get(Option.ARCADE_EMULATOR)
        if not driver:
            driver = "mame-fs"

        if driver == "mame":
            return MameArcadeDriver(fsgc)
        elif driver == "mame-fs":
            return MameArcadeDriver(fsgc, fsemu=True)

        return None

    def loader(self, fsgc):
        return ArcadeLoader(fsgc)


class ArcadeLoader(SimpleLoader):
    def load_files(self, values):
        # file_list = json.loads(values["file_list"])
        # assert len(file_list) == 1
        # self.config["cartridge"] = "sha1://{0}/{1}".format(
        #     file_list[0]["sha1"], file_list[0]["name"])
        self.config["file_list"] = values["file_list"]

    def load_extra(self, values):
        if "refresh_rate" in values:
            self.config["refresh_rate"] = values["refresh_rate"]
        if "orientation" in values:
            self.config["orientation"] = values["orientation"]
        self.config["mame_rom_set"] = values["mame_rom_set"]
