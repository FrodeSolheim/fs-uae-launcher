from fsgs.platform import PlatformHandler
from fsgs.platforms.a5200.messa5200driver import MessA5200Driver
from fsgs.platforms.loader import SimpleLoader


class Atari5200PlatformHandler(PlatformHandler):
    PLATFORM_NAME = "Atari 5200"

    def __init__(self):
        PlatformHandler.__init__(self)

    def get_loader(self, fsgs):
        return Atari5200Loader(fsgs)

    def get_runner(self, fsgs):
        return MessA5200Driver(fsgs)


class Atari5200Loader(SimpleLoader):
    pass
