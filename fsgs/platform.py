from fsbc.util import memoize


class Platform(object):

    pass


class PlatformHandler(object):

    def __init__(self):
        pass

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
            return UnsupportedPlatformHandler

    @classmethod
    @memoize
    def get_platform_name(cls, platform_id):
        return cls.get_platform_class(platform_id).PLATFORM_NAME

    @classmethod
    @memoize
    def get_platform_ids(cls):
        return sorted(platforms.keys())


class UnsupportedPlatformHandler(PlatformHandler):

    PLATFORM_NAME = "Unsupported"


from .platforms.amiga import AmigaPlatformHandler
from .platforms.amstrad_cpc import AmstradCPCPlatformHandler
from .platforms.arcade import ArcadePlatformHandler
from .platforms.atari_2600 import Atari2600PlatformHandler
from .platforms.atari_5200 import Atari5200PlatformHandler
from .platforms.atari_7800 import Atari7800PlatformHandler
from .platforms.atari_st import AtariSTPlatformHandler
from .platforms.cdtv import CDTVPlatformHandler
from .platforms.cd32 import CD32PlatformHandler
from .platforms.commodore_64 import Commodore64PlatformHandler
from .platforms.dos import DOSPlatformHandler
from .platforms.game_boy import GameBoyPlatformHandler
from .platforms.game_boy_advance import GameBoyAdvancePlatformHandler
from .platforms.game_boy_color import GameBoyColorPlatformHandler
from .platforms.game_gear import GameGearPlatformHandler
from .platforms.lynx import LynxPlatformHandler
from .platforms.master_system import MasterSystemPlatformHandler
from .platforms.mega_drive import MegaDrivePlatformHandler
from .platforms.nintendo import NintendoPlatformHandler
from .platforms.super_nintendo import SuperNintendoPlatformHandler
from .platforms.turbografx_16 import TurboGrafx16PlatformHandler
from .platforms.zx_spectrum import ZXSpectrumPlatformHandler


platforms = {
    "amiga": AmigaPlatformHandler,
    "amstrad-cpc": AmstradCPCPlatformHandler,
    "arcade": ArcadePlatformHandler,
    "atari-2600": Atari2600PlatformHandler,
    "atari-5200": Atari5200PlatformHandler,
    "atari-7800": Atari7800PlatformHandler,
    "atari-st": AtariSTPlatformHandler,
    "cd32": CD32PlatformHandler,
    "cdtv": CDTVPlatformHandler,
    "commodore-64": Commodore64PlatformHandler,
    "dos": DOSPlatformHandler,
    "game-boy": GameBoyPlatformHandler,
    "gba": GameBoyAdvancePlatformHandler,
    "game-boy-color": GameBoyColorPlatformHandler,
    "game-gear": GameGearPlatformHandler,
    "lynx": LynxPlatformHandler,
    "master-system": MasterSystemPlatformHandler,
    "mega-drive": MegaDrivePlatformHandler,
    "nes": NintendoPlatformHandler,
    "snes": SuperNintendoPlatformHandler,
    "turbografx-16": TurboGrafx16PlatformHandler,
    "zx-spectrum": ZXSpectrumPlatformHandler,

    # Aliases
    "game-boy-advance": GameBoyAdvancePlatformHandler,
    "nintendo": NintendoPlatformHandler,
    "super-nintendo": SuperNintendoPlatformHandler,
}


def normalize_platform_id(platform_id):
    platform_id = platform_id.lower().replace("-", "").replace("_", "")
    # noinspection SpellCheckingInspection
    if platform_id in ["commodorecdtv"]:
        return "cdtv"
    elif platform_id in ["amigacd32"]:
        return "cd32"
    elif platform_id in ["msdos"]:
        return "dos"
    elif platform_id in ["gameboyadvance"]:
        return "gba"
    elif platform_id in ["nintendo", "famicom"]:
        return "nes"
    elif platform_id in ["supernintendo", "supernes", "superfamicom"]:
        return "snes"
    return platform_id
