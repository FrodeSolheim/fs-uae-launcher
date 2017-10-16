from fsgs.knownfiles import KnownFile
from fsgs.platform import PlatformHandler
from fsgs.platforms.loader import SimpleLoader

PSX_PLATFORM_ID = "PSX"
PSX_PLATFORM_NAME = "PlayStation"
# noinspection SpellCheckingInspection
PSX_SCPH5500_BIN_SHA1 = "b05def971d8ec59f346f2d9ac21fb742e3eb6917"
# noinspection SpellCheckingInspection
PSX_SCPH5501_BIN_SHA1 = "0555c6fae8906f3f09baf5988f00e55f88e9f30b"
# noinspection SpellCheckingInspection
PSX_SCPH5502_BIN_SHA1 = "f6bc2d1f5eb6593de7d089c425ac681d6fffd3f0"
PSX_CONTROLLER = {
    "type": "gamepad",
    "description": "Gamepad",
    "mapping_name": "playstation",
}
PSX_SCPH5500_BIN = KnownFile(
    "b05def971d8ec59f346f2d9ac21fb742e3eb6917", PSX_PLATFORM_ID,
    "scph5500.bin")
PSX_SCPH5501_BIN = KnownFile(
    "0555c6fae8906f3f09baf5988f00e55f88e9f30b", PSX_PLATFORM_ID,
    "scph5501.bin")
# noinspection SpellCheckingInspection
PSX_SCPH5502_BIN = KnownFile(
    "f6bc2d1f5eb6593de7d089c425ac681d6fffd3f0", PSX_PLATFORM_ID,
    "scph5502.bin")
PSX_ROMS_FOR_REGION = {
    "JA": ["scph5500.bin", PSX_SCPH5500_BIN.sha1],
    "US": ["scph5501.bin", PSX_SCPH5501_BIN.sha1],
    "EU": ["scph5502.bin", PSX_SCPH5502_BIN.sha1],
}


class PlayStationPlatformHandler(PlatformHandler):
    # FIXME: Move to init instead
    PLATFORM_NAME = PSX_PLATFORM_NAME

    def __init__(self):
        PlatformHandler.__init__(self)

    def get_loader(self, fsgs):
        return PlayStationLoader(fsgs)

    def get_runner(self, fsgs):
        from fsgs.platforms.psx.psxmednafendriver import PlayStationMednafenDriver
        return PlayStationMednafenDriver(fsgs)


class PlayStationLoader(SimpleLoader):
    def load_files(self, values):
        self.config["cue_sheets"] = values["cue_sheets"]
        self.config["file_list"] = values["file_list"]
