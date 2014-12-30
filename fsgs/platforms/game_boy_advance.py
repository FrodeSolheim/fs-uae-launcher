from fsgs.platform import PlatformHandler
from fsgs.mednafen.game_boy_advance import GameBoyAdvanceRunner
from .loader import SimpleLoader


class GameBoyAdvancePlatformHandler(PlatformHandler):

    PLATFORM_NAME = "Game Boy Advance"

    def __init__(self):
        PlatformHandler.__init__(self)

    def get_loader(self, fsgs):
        return GameBoyAdvanceLoader(fsgs)

    def get_runner(self, fsgs):
        return GameBoyAdvanceRunner(fsgs)


class GameBoyAdvanceLoader(SimpleLoader):
    pass
