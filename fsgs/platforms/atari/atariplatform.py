import json

from fsgs.option import Option
from fsgs.platform import PlatformHandler
from fsgs.platforms.atari.hatariataridriver import HatariAtariDriver, \
    ATARI_MODEL_1040ST
from fsgs.platforms.loader import SimpleLoader


class AtariSTPlatformHandler(PlatformHandler):
    PLATFORM_NAME = "Atari ST"

    def __init__(self):
        PlatformHandler.__init__(self)

    def get_loader(self, fsgs):
        return AtariSTLoader(fsgs)

    def get_runner(self, fsgs):
        return HatariAtariDriver(fsgs)


class AtariSTLoader(SimpleLoader):
    def load_files(self, values):
        file_list = json.loads(values["file_list"])
        # assert len(file_list) == 1
        if file_list[0]["name"].endswith(".st"):
            self.config["floppy_drive_0"] = "sha1://{0}/{1}".format(
                file_list[0]["sha1"], file_list[0]["name"])
        if file_list[0]["name"].endswith(".stx"):
            self.config["floppy_drive_0"] = "sha1://{0}/{1}".format(
                file_list[0]["sha1"], file_list[0]["name"])

    def load_extra(self, values):
        self.config[Option.ATARI_MODEL] = values["model"]
        if not self.config[Option.ATARI_MODEL]:
            self.config[Option.ATARI_MODEL] = ATARI_MODEL_1040ST
