from fsgs.platform import PlatformHandler
from fsgs.platforms.loader import SimpleLoader
from fsgs.platforms.snes.mednafensnesdriver import MednafenSnesDriver


class SuperNintendoPlatformHandler(PlatformHandler):
    PLATFORM_NAME = "Super Nintendo"

    def __init__(self):
        PlatformHandler.__init__(self)

    def get_loader(self, fsgs):
        return SuperNintendoLoader(fsgs)

    def get_runner(self, fsgs):
        return MednafenSnesDriver(fsgs)


class SuperNintendoLoader(SimpleLoader):
    pass
