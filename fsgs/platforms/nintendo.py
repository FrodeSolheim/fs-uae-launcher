from fsbc import settings
from fsgs.drivers.mess.messnesdriver import MessNesDriver
from fsgs.option import Option
from fsgs.platform import PlatformHandler
from fsgs.platforms.loader import SimpleLoader
from fsgs.platforms.nes.mednafennesdriver import MednafenNesDriver


class NintendoPlatformHandler(PlatformHandler):
    PLATFORM_NAME = "Nintendo"

    def __init__(self):
        PlatformHandler.__init__(self)

    def get_loader(self, fsgs):
        return NintendoLoader(fsgs)

    def get_runner(self, fsgs):
        if settings.get(Option.NES_DRIVER) == "mess":
            return MessNesDriver(fsgs)
        else:
            return MednafenNesDriver(fsgs)


class NintendoLoader(SimpleLoader):
    def load_extra(self, values):
        self.config["ines_header"] = values["ines_header"]
