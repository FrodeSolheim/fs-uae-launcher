from fsgs.platform import PlatformHandler
from fsgs.amiga.valueconfigloader import ValueConfigLoader
from fsgs.amiga.fsuaeamigadriver import FSUAEAmigaDriver


class AmigaPlatformHandler(PlatformHandler):
    PLATFORM_NAME = "Amiga"

    def __init__(self):
        PlatformHandler.__init__(self)

    def get_loader(self, fsgs):
        loader = ValueConfigLoader()
        loader.uuid = fsgs.game.variant.uuid
        return loader

    def get_runner(self, fsgs):
        return FSUAEAmigaDriver(fsgs)
