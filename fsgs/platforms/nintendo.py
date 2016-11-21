from fsgs.mednafen.nintendo import NintendoRunner
from fsgs.platform import PlatformHandler
from fsgs.platforms.loader import SimpleLoader


class NintendoPlatformHandler(PlatformHandler):
    PLATFORM_NAME = "Nintendo E.S."

    def __init__(self):
        PlatformHandler.__init__(self)

    def get_loader(self, fsgs):
        return NintendoLoader(fsgs)

    def get_runner(self, fsgs):
        return NintendoRunner(fsgs)


class NintendoLoader(SimpleLoader):
    pass
