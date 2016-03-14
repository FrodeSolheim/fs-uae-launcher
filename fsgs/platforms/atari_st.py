import json

from fsgs.drivers.atari import AtariDriver
from fsgs.platform import PlatformHandler
from .loader import SimpleLoader


class AtariSTPlatformHandler(PlatformHandler):

    PLATFORM_NAME = "Atari ST"

    def __init__(self):
        PlatformHandler.__init__(self)

    def get_loader(self, fsgs):
        return AtariSTLoader(fsgs)

    def get_runner(self, fsgs):
        return AtariDriver(fsgs)


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
