from fsgs.platform import PlatformHandler
from fsgs.mednafen.game_boy import GameBoyRunner
from .loader import SimpleLoader


class GameBoyPlatformHandler(PlatformHandler):

    PLATFORM_NAME = "Game Boy"

    def __init__(self):
        PlatformHandler.__init__(self)

    def get_loader(self, fsgs):
        return GameBoyLoader(fsgs)

    def get_runner(self, fsgs):
        return GameBoyRunner(fsgs)


class GameBoyLoader(SimpleLoader):
    pass
