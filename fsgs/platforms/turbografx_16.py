from fsgs.platform import PlatformHandler
from fsgs.mednafen.turbografx_16 import TurboGrafx16Runner
from .loader import SimpleLoader


class TurboGrafx16PlatformHandler(PlatformHandler):

    PLATFORM_NAME = "TurboGrafx-16"

    def __init__(self):
        PlatformHandler.__init__(self)

    def get_loader(self, fsgs):
        return TurboGrafx16Loader(fsgs)

    def get_runner(self, fsgs):
        return TurboGrafx16Runner(fsgs)


class TurboGrafx16Loader(SimpleLoader):
    pass
