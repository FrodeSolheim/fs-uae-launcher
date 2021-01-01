import json

from fsbc import settings
from fsgs.options.option import Option
from fsgs.platform import Platform
from fsgs.platforms.atari.hatariataridriver import (
    HatariDriver,
    HatariFsDriver,
    ST_MODEL_1040STFM,
)
from fsgs.platforms.loader import SimpleLoader


class AtariSTPlatform(Platform):
    PLATFORM_NAME = "Atari ST"

    def driver(self, fsgc):
        driver = settings.get(Option.ST_EMULATOR)
        if not driver:
            driver = "hatari-fs"

        if driver == "hatari":
            return HatariDriver(fsgc)
        elif driver == "hatari-fs":
            return HatariFsDriver(fsgc)

        return None

    def loader(self, fsgc):
        return AtariSTLoader(fsgc)


class AtariSTLoader(SimpleLoader):
    def load_files(self, values):
        file_list = json.loads(values["file_list"])
        # assert len(file_list) == 1
        if file_list[0]["name"].endswith(".st"):
            self.config["floppy_drive_0"] = "sha1://{0}/{1}".format(
                file_list[0]["sha1"], file_list[0]["name"]
            )
        if file_list[0]["name"].endswith(".stx"):
            self.config["floppy_drive_0"] = "sha1://{0}/{1}".format(
                file_list[0]["sha1"], file_list[0]["name"]
            )

    def load_extra(self, values):
        # self.config[Option.ST_MODEL] = values["model"]
        self.config[Option.ST_MODEL] = values["st_model"]
        self.config[Option.PLATFORM] = "st"  # FIXME: Deprecated

        if not self.config[Option.ST_MODEL]:
            self.config[Option.ST_MODEL] = ST_MODEL_1040STFM
