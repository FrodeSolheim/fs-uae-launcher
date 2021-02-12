from fsgamesys.amiga.fsuaeamigadriver import FSUAEAmigaDriver
from fsgamesys.amiga.valueconfigloader import ValueConfigLoader
from fsgamesys.drivers.gamedriver import GameDriver
from fsgamesys.platforms.platform import PlatformHandler


class AmigaPlatformHandler(PlatformHandler):
    PLATFORM_NAME = "Amiga"

    def __init__(self):
        PlatformHandler.__init__(self)

    def get_loader(self, fsgs):
        loader = ValueConfigLoader()
        loader.uuid = fsgs.game.variant.uuid
        return loader

    def get_runner(self, fsgs) -> GameDriver:
        return FSUAEAmigaDriver(fsgs)
