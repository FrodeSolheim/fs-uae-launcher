import json
import os
from functools import lru_cache

from fsgs.drivers.c64 import C64Driver


class Platform(object):
    pass


class PlatformHandler(object):
    def __init__(self, loader_class=None, runner_class=None):
        self.loader_class = loader_class
        self.runner_class = runner_class

    @classmethod
    def create(cls, platform_id):
        class_ = cls.get_platform_class(platform_id)
        return class_()

    @classmethod
    def get_platform_class(cls, platform_id):
        platform_id = platform_id.lower()
        try:
            return platforms[platform_id]
        except KeyError:
            return UnsupportedPlatform

    @classmethod
    @lru_cache()
    def get_platform_name(cls, platform_id):
        return cls.get_platform_class(platform_id).PLATFORM_NAME

    @classmethod
    @lru_cache()
    def get_platform_ids(cls):
        return sorted(platforms.keys())

    def get_loader(self, fsgs):
        if self.loader_class is None:
            raise Exception("loader class is None for " + repr(self))
        return self.loader_class(fsgs)

    def get_runner(self, fsgs):
        if self.runner_class is None:
            raise Exception("runner class is None for " + repr(self))
        return self.runner_class(fsgs)


from fsgs.platforms.amiga import AmigaPlatformHandler
from fsgs.platforms.amstrad_cpc import AmstradCPCPlatformHandler
from fsgs.platforms.arcade import ArcadePlatformHandler
from fsgs.platforms.atari_2600 import Atari2600PlatformHandler
from fsgs.platforms.atari_5200 import Atari5200PlatformHandler
from fsgs.platforms.atari_7800 import Atari7800PlatformHandler
from fsgs.platforms.atari_st import AtariSTPlatformHandler
from fsgs.platforms.cd32 import CD32PlatformHandler
from fsgs.platforms.cdtv import CDTVPlatformHandler
from fsgs.platforms.dos import DOSPlatformHandler
from fsgs.platforms.game_boy import GameBoyPlatformHandler
from fsgs.platforms.game_boy_advance import GameBoyAdvancePlatformHandler
from fsgs.platforms.game_boy_color import GameBoyColorPlatformHandler
from fsgs.platforms.game_gear import GameGearPlatformHandler
from fsgs.platforms.loader import SimpleLoader
from fsgs.platforms.lynx import LynxPlatformHandler
from fsgs.platforms.master_system import MasterSystemPlatformHandler
from fsgs.platforms.mega_drive import MegaDrivePlatformHandler
from fsgs.platforms.nintendo import NintendoPlatformHandler
from fsgs.platforms.psx import PlayStationPlatformHandler
from fsgs.platforms.super_nintendo import SuperNintendoPlatformHandler
from fsgs.platforms.turbografx_16 import TurboGrafx16PlatformHandler
from fsgs.platforms.zx_spectrum import ZXSpectrumPlatformHandler


class UnsupportedPlatform(PlatformHandler):
    PLATFORM_NAME = "Unsupported"


class C64Loader(SimpleLoader):
    def load_files(self, values):
        file_list = json.loads(values["file_list"])
        # assert len(file_list) == 1
        for i, item in enumerate(file_list):
            _, ext = os.path.splitext(item["name"])
            if ext in [".tap"]:
                if i == 0:
                    self.config["tape_drive_0"] = "sha1://{0}/{1}".format(
                        item["sha1"], item["name"])
                self.config["tape_image_{0}".format(i)] = \
                    "sha1://{0}/{1}".format(item["sha1"], item["name"])
            elif ext in [".d64"]:
                if i == 0:
                    self.config["floppy_drive_0"] = "sha1://{0}/{1}".format(
                        item["sha1"], item["name"])
                self.config["floppy_image_{0}".format(i)] = \
                    "sha1://{0}/{1}".format(item["sha1"], item["name"])


class C64Platform(PlatformHandler):
    PLATFORM_NAME = "Commodore 64"

    def __init__(self):
        super().__init__(C64Loader, C64Driver)


platforms = {
    "amiga": AmigaPlatformHandler,
    "arcade": ArcadePlatformHandler,
    "atari-2600": Atari2600PlatformHandler,
    "atari-5200": Atari5200PlatformHandler,
    "atari-7800": Atari7800PlatformHandler,
    "atari": AtariSTPlatformHandler,
    "c64": C64Platform,
    "cd32": CD32PlatformHandler,
    "cdtv": CDTVPlatformHandler,
    "cpc": AmstradCPCPlatformHandler,
    "dos": DOSPlatformHandler,
    "gb": GameBoyPlatformHandler,
    "gba": GameBoyAdvancePlatformHandler,
    "gbc": GameBoyColorPlatformHandler,
    "game-gear": GameGearPlatformHandler,
    "lynx": LynxPlatformHandler,
    "master-system": MasterSystemPlatformHandler,
    "mega-drive": MegaDrivePlatformHandler,
    "nes": NintendoPlatformHandler,
    "snes": SuperNintendoPlatformHandler,
    "psx": PlayStationPlatformHandler,
    "turbografx-16": TurboGrafx16PlatformHandler,
    "zx-spectrum": ZXSpectrumPlatformHandler,
}


def normalize_platform_id(platform_id):
    platform_id = platform_id.lower().replace("-", "").replace("_", "")
    # noinspection SpellCheckingInspection
    if platform_id in ["st", "atarist"]:
        return "atari"
    elif platform_id in ["commodorecdtv"]:
        return "cdtv"
    elif platform_id in ["amigacd32"]:
        return "cd32"
    elif platform_id in ["amstradcpc"]:
        return "cpc"
    elif platform_id in ["msdos"]:
        return "dos"
    elif platform_id in ["gameboy"]:
        return "gb"
    elif platform_id in ["gameboyadvance"]:
        return "gba"
    elif platform_id in ["gameboycolor"]:
        return "gbc"
    elif platform_id in ["nintendo", "famicom"]:
        return "nes"
    elif platform_id in ["supernintendo", "supernes", "superfamicom"]:
        return "snes"
    return platform_id
