from fsgs.drivers.mess.messmsxdriver import MessMsxDriver
from fsgs.platform import PlatformHandler
from fsgs.platforms.loader import SimpleLoader


class MsxPlatformHandler(PlatformHandler):
    PLATFORM_NAME = "MSX"

    def __init__(self):
        PlatformHandler.__init__(self)

    def get_loader(self, fsgs):
        return MsxLoader(fsgs)

    def get_runner(self, fsgs):
        return MessMsxDriver(fsgs)


class MsxLoader(SimpleLoader):
    pass
