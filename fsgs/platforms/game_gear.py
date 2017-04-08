from fsgs.drivers.mednafen.gamegeardriver import MednafenGameGearDriver
from fsgs.platform import PlatformHandler
from .loader import SimpleLoader


class GameGearPlatformHandler(PlatformHandler):
    PLATFORM_NAME = "Game Gear"

    def __init__(self):
        PlatformHandler.__init__(self)

    def get_loader(self, fsgs):
        return GameGearLoader(fsgs)

    def get_runner(self, fsgs):
        return MednafenGameGearDriver(fsgs)


class GameGearLoader(SimpleLoader):
    pass
