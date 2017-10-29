from functools import lru_cache

from fsgs.drivers.gamedriver import GameDriver


class PlatformHandler:
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

    def get_runner(self, fsgs) -> GameDriver:
        if self.runner_class is None:
            raise Exception("runner class is None for " + repr(self))
        return self.runner_class(fsgs)

    def driver(self, fsgc):
        return self.get_runner(fsgc)

    def loader(self, fsgc):
        return self.get_loader(fsgc)


class Platform(PlatformHandler):
    AMIGA = "amiga"
    ARCADE = "arcade"
    A2600 = "a2600"
    A5200 = "a5200"
    A7800 = "a7800"
    ATARI = "atari"
    C64 = "c64"
    CD32 = "cd32"
    CDTV = "cdtv"
    CPC = "cpc"
    DOS = "dos"
    GB = "gb"
    GBA = "gba"
    GBC = "gbc"
    GAME_GEAR = "game-gear"
    LYNX = "lynx"
    MSX = "msx"
    N64 = "n64"
    NEOGEO = "neogeo"
    NES = "nes"
    NGC = "ngc"
    PSX = "psx"
    SNES = "snes"
    SMD = "smd"
    SMS = "sms"
    TG16 = "tg16"
    TGCD = "tgcd"
    ZXS = "zxs"

    def get_loader(self, fsgc):
        return self.loader(fsgc)

    def get_runner(self, fsgc):
        return self.driver(fsgc)

    def driver(self, fsgc):
        raise NotImplementedError()

    def loader(self, fsgc):
        raise NotImplementedError()


from fsgs.platforms.amiga import AmigaPlatformHandler
from fsgs.platforms.amstrad_cpc import AmstradCPCPlatformHandler
from fsgs.platforms.arcade.arcadeplatform import ArcadePlatformHandler
from fsgs.platforms.atari_2600 import Atari2600PlatformHandler
from fsgs.platforms.atari5200 import Atari5200PlatformHandler
from fsgs.platforms.atari_7800 import Atari7800PlatformHandler
from fsgs.platforms.atari.atariplatform import AtariSTPlatformHandler
from fsgs.platforms.cd32 import CD32PlatformHandler
from fsgs.platforms.cdtv import CDTVPlatformHandler
from fsgs.platforms.commodore64 import Commodore64Platform
from fsgs.platforms.dos.dosplatform import DOSPlatformHandler
from fsgs.platforms.game_boy import GameBoyPlatformHandler
from fsgs.platforms.game_boy_advance import GameBoyAdvancePlatformHandler
from fsgs.platforms.game_boy_color import GameBoyColorPlatformHandler
from fsgs.platforms.game_gear import GameGearPlatformHandler
from fsgs.platforms.lynx import LynxPlatformHandler
from fsgs.platforms.master_system import MasterSystemPlatformHandler
from fsgs.platforms.megadrive import MegaDrivePlatform
from fsgs.platforms.msx import MsxPlatformHandler
from fsgs.platforms.nintendo64 import Nintendo64Platform
from fsgs.platforms.neogeo import NeoGeoPlatform
from fsgs.platforms.ngc.ngcplatform import NGCPlatformHandler
from fsgs.platforms.nintendo import NintendoPlatform
from fsgs.platforms.psx.psxplatform import PlayStationPlatformHandler
from fsgs.platforms.supernintendo import SuperNintendoPlatformHandler
from fsgs.platforms.turbografx16 import TurboGrafx16Platform
from fsgs.platforms.turbografxcd import TurboGrafxCDPlatform
from fsgs.platforms.zxs import SpectrumPlatformHandler


class UnsupportedPlatform(PlatformHandler):
    PLATFORM_NAME = "Unsupported"


platforms = {
    Platform.AMIGA: AmigaPlatformHandler,
    Platform.ARCADE: ArcadePlatformHandler,
    Platform.A2600: Atari2600PlatformHandler,
    Platform.A5200: Atari5200PlatformHandler,
    Platform.A7800: Atari7800PlatformHandler,
    Platform.ATARI: AtariSTPlatformHandler,
    Platform.C64: Commodore64Platform,
    Platform.CD32: CD32PlatformHandler,
    Platform.CDTV: CDTVPlatformHandler,
    Platform.CPC: AmstradCPCPlatformHandler,
    Platform.DOS: DOSPlatformHandler,
    Platform.GB: GameBoyPlatformHandler,
    Platform.GBA: GameBoyAdvancePlatformHandler,
    Platform.GBC: GameBoyColorPlatformHandler,
    Platform.GAME_GEAR: GameGearPlatformHandler,
    Platform.LYNX: LynxPlatformHandler,
    Platform.MSX: MsxPlatformHandler,
    Platform.N64: Nintendo64Platform,
    Platform.NEOGEO: NeoGeoPlatform,
    Platform.NES: NintendoPlatform,
    Platform.NGC: NGCPlatformHandler,
    Platform.SNES: SuperNintendoPlatformHandler,
    Platform.PSX: PlayStationPlatformHandler,
    Platform.SMD: MegaDrivePlatform,
    Platform.SMS: MasterSystemPlatformHandler,
    Platform.TG16: TurboGrafx16Platform,
    Platform.TGCD: TurboGrafxCDPlatform,
    Platform.ZXS: SpectrumPlatformHandler,
}
PLATFORM_IDS = platforms.keys()


def normalize_platform_id(platform_id):
    platform_id = platform_id.lower().replace("-", "").replace("_", "")
    # noinspection SpellCheckingInspection
    if platform_id in ["st", "atarist"]:
        return Platform.ATARI
    elif platform_id in ["commodorecdtv"]:
        return Platform.CDTV
    elif platform_id in ["amigacd32"]:
        return Platform.CD32
    elif platform_id in ["amstradcpc"]:
        return Platform.CPC
    elif platform_id in ["msdos"]:
        return Platform.DOS
    elif platform_id in ["gameboy"]:
        return Platform.GB
    elif platform_id in ["gameboyadvance"]:
        return Platform.GBA
    elif platform_id in ["gameboycolor"]:
        return Platform.GBC
    elif platform_id in ["nintendo", "famicom"]:
        return Platform.NES
    elif platform_id in ["nintendo64"]:
        return Platform.N64
    elif platform_id in ["nintendogamecube", "gamecube", "gc"]:
        return Platform.NGC
    elif platform_id in ["supernintendo", "supernes", "superfamicom"]:
        return Platform.SNES
    elif platform_id in ["zxspectrum"]:
        return Platform.ZXS
    elif platform_id in ["mastersystem", "segamastersystem"]:
        return Platform.SMS
    elif platform_id in ["megadrive", "segamegadrive", "genesis"]:
        return Platform.SMD
    elif platform_id in ["atari2600"]:
        return Platform.A2600
    elif platform_id in ["atari5200"]:
        return Platform.A5200
    elif platform_id in ["atari78600"]:
        return Platform.A7800
    elif platform_id in ["turbografx16"]:
        return Platform.TG16
    return platform_id
