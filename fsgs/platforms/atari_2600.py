from fsgs.platform import PlatformHandler
from fsgs.platforms.a2600.messa2600driver import MessA2600Driver
from fsgs.platforms.loader import SimpleLoader


class Atari2600PlatformHandler(PlatformHandler):
    PLATFORM_NAME = "Atari 2600"

    def __init__(self):
        PlatformHandler.__init__(self)

    def get_loader(self, fsgs):
        return Atari2600Loader(fsgs)

    def get_runner(self, fsgs):
        return MessA2600Driver(fsgs)


class Atari2600Loader(SimpleLoader):
    pass
