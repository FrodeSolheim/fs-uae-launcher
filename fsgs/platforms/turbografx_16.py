from fsgs.platform import PlatformHandler
from fsgs.platforms.loader import SimpleLoader
from fsgs.platforms.tg16.mednafentg16driver import MednafenTg16Driver


class TurboGrafx16PlatformHandler(PlatformHandler):
    PLATFORM_NAME = "TurboGrafx-16"

    def __init__(self):
        PlatformHandler.__init__(self)

    def get_loader(self, fsgs):
        return TurboGrafx16Loader(fsgs)

    def get_runner(self, fsgs):
        return MednafenTg16Driver(fsgs)


class TurboGrafx16Loader(SimpleLoader):
    pass
