from fsgs.platform import PlatformHandler
from fsgs.platforms.loader import SimpleLoader

NGC_PLATFORM_NAME = "GameCube"
NGC_CONTROLLER = {
    "type": "gamepad",
    "description": "Gamepad",
    "mapping_name": "ngc",
}


class NGCPlatformHandler(PlatformHandler):
    # FIXME: Move to init instead
    PLATFORM_NAME = NGC_PLATFORM_NAME

    def __init__(self):
        PlatformHandler.__init__(self)

    def get_loader(self, fsgs):
        return NGCLoader(fsgs)

    def get_runner(self, fsgs):
        from fsgs.platforms.ngc.ngcdriver import NGCDriver
        return NGCDriver(fsgs)


class NGCLoader(SimpleLoader):
    pass