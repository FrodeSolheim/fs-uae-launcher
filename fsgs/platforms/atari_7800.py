from fsgs.platform import PlatformHandler
from fsgs.platforms.a7800.messa7800driver import MessA7800Driver
from fsgs.platforms.loader import SimpleLoader


class Atari7800PlatformHandler(PlatformHandler):
    PLATFORM_NAME = "Atari 7800"

    def __init__(self):
        PlatformHandler.__init__(self)

    def get_loader(self, fsgs):
        return Atari7800Loader(fsgs)

    def get_runner(self, fsgs):
        return MessA7800Driver(fsgs)


class Atari7800Loader(SimpleLoader):
    pass
