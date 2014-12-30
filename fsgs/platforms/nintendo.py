from fsgs.platform import PlatformHandler
from fsgs.mednafen.nintendo import NintendoRunner
from .loader import SimpleLoader


class NintendoPlatformHandler(PlatformHandler):

    PLATFORM_NAME = "Nintendo"

    def __init__(self):
        PlatformHandler.__init__(self)

    def get_loader(self, fsgs):
        return NintendoLoader(fsgs)

    def get_runner(self, fsgs):
        return NintendoRunner(fsgs)


class NintendoLoader(SimpleLoader):
    pass
