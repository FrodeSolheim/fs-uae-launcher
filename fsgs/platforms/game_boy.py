from fsgs.platform import PlatformHandler
from fsgs.platforms.gb.mednafengbdriver import MednafenGbDriver
from fsgs.platforms.loader import SimpleLoader


class GameBoyPlatformHandler(PlatformHandler):
    PLATFORM_NAME = "Game Boy"

    def __init__(self):
        PlatformHandler.__init__(self)

    def get_loader(self, fsgs):
        return GameBoyLoader(fsgs)

    def get_runner(self, fsgs):
        return MednafenGbDriver(fsgs)


class GameBoyLoader(SimpleLoader):
    pass
