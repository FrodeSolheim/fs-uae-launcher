from fsgs.platform import PlatformHandler
from fsgs.platforms.gbc.mednafengbcdriver import MednafenGbcDriver
from fsgs.platforms.loader import SimpleLoader


class GameBoyColorPlatformHandler(PlatformHandler):
    PLATFORM_NAME = "Game Boy Color"

    def __init__(self):
        PlatformHandler.__init__(self)

    def get_loader(self, fsgs):
        return GameBoyColorLoader(fsgs)

    def get_runner(self, fsgs):
        return MednafenGbcDriver(fsgs)


class GameBoyColorLoader(SimpleLoader):
    pass
