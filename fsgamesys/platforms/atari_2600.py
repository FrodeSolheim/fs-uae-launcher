from fsgamesys.platforms.a2600.messa2600driver import MessA2600Driver
from fsgamesys.platforms.loader import SimpleLoader
from fsgamesys.platforms.platform import PlatformHandler


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
