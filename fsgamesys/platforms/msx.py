from fsgamesys.drivers.mess.messmsxdriver import MessMsxDriver
from fsgamesys.platforms.loader import SimpleLoader
from fsgamesys.platforms.platform import PlatformHandler


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
