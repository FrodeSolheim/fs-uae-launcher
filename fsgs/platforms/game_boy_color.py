from fsgs.platform import PlatformHandler
from fsgs.mednafen.game_boy_color import GameBoyColorRunner
from .loader import SimpleLoader


class GameBoyColorPlatformHandler(PlatformHandler):

    PLATFORM_NAME = "Game Boy Color"

    def __init__(self):
        PlatformHandler.__init__(self)

    def get_loader(self, fsgs):
        return GameBoyColorLoader(fsgs)

    def get_runner(self, fsgs):
        return GameBoyColorRunner(fsgs)


class GameBoyColorLoader(SimpleLoader):
    pass
