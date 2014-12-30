from fsgs.platform import PlatformHandler
from fsgs.mednafen.mega_drive import MegaDriveRunner
from .loader import SimpleLoader


class MegaDrivePlatformHandler(PlatformHandler):

    PLATFORM_NAME = "Mega Drive"

    def __init__(self):
        PlatformHandler.__init__(self)

    def get_loader(self, fsgs):
        return MegaDriveLoader(fsgs)

    def get_runner(self, fsgs):
        return MegaDriveRunner(fsgs)


class MegaDriveLoader(SimpleLoader):
    pass
