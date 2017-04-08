from fsgs.platform import PlatformHandler
from fsgs.platforms.gba.mednafengbadriver import MednafenGbaDriver
from fsgs.platforms.loader import SimpleLoader


class GameBoyAdvancePlatformHandler(PlatformHandler):
    PLATFORM_NAME = "Game Boy Advance"

    def __init__(self):
        PlatformHandler.__init__(self)

    def get_loader(self, fsgs):
        return GameBoyAdvanceLoader(fsgs)

    def get_runner(self, fsgs):
        return MednafenGbaDriver(fsgs)


class GameBoyAdvanceLoader(SimpleLoader):
    def load_extra(self, values):
        self.config["sram_type"] = values["sram_type"]
