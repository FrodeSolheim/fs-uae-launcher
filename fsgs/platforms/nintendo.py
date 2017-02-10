from fsgs.mednafen.nes import MednafenNintendoDriver
from fsgs.platform import PlatformHandler
from fsgs.platforms.loader import SimpleLoader


class NintendoPlatformHandler(PlatformHandler):
    PLATFORM_NAME = "Nintendo"

    def __init__(self):
        PlatformHandler.__init__(self)

    def get_loader(self, fsgs):
        return NintendoLoader(fsgs)

    def get_runner(self, fsgs):
        return MednafenNintendoDriver(fsgs)


class NintendoLoader(SimpleLoader):
    def load_extra(self, values):
        self.config["ines_header"] = values["ines_header"]
