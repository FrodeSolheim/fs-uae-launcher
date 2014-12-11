from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

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
