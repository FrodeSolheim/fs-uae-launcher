from fsgs.platform import PlatformHandler
from fsgs.mess.atari_5200 import Atari5200Runner
from .loader import SimpleLoader


class Atari5200PlatformHandler(PlatformHandler):

    PLATFORM_NAME = "Atari 5200"

    def __init__(self):
        PlatformHandler.__init__(self)

    def get_loader(self, fsgs):
        return Atari5200Loader(fsgs)

    def get_runner(self, fsgs):
        return Atari5200Runner(fsgs)


class Atari5200Loader(SimpleLoader):
    pass
