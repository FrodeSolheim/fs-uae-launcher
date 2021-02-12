from functools import lru_cache

from fsgamesys.drivers.gamedriver import GameDriver


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
    # ATARI = "atari"
    C64 = "c64"
    CD32 = "cd32"
    CDTV = "cdtv"
    CPC = "cpc"
    DOS = "dos"
    GB = "gb"
    GBA = "gba"
    GBC = "gbc"
    LYNX = "lynx"
    MSX = "msx"
    N64 = "n64"
    NDS = "nds"
    NEOGEO = "neogeo"
    NES = "nes"
    NGC = "ngc"
    PSX = "psx"
    SGG = "sgg"
    SMD = "smd"
    SMS = "sms"
    SNES = "snes"
    SPECTRUM = "spectrum"
    ST = "st"
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


from fsgamesys.platforms.amiga import AmigaPlatformHandler
from fsgamesys.platforms.cpc.cpcplatform import CpcPlatform
from fsgamesys.platforms.arcade.arcadeplatform import ArcadePlatformHandler
from fsgamesys.platforms.atari_2600 import Atari2600PlatformHandler
from fsgamesys.platforms.atari5200 import Atari5200PlatformHandler
from fsgamesys.platforms.atari7800 import Atari7800PlatformHandler
from fsgamesys.platforms.atari.atariplatform import AtariSTPlatform
from fsgamesys.platforms.cd32 import CD32PlatformHandler
from fsgamesys.platforms.cdtv import CDTVPlatformHandler
from fsgamesys.platforms.commodore64 import Commodore64Platform
from fsgamesys.platforms.dos.dosplatform import DOSPlatformHandler
from fsgamesys.platforms.gameboy import GameBoyPlatform
from fsgamesys.platforms.gameboyadvance import GameBoyAdvancePlatform
from fsgamesys.platforms.gameboycolor import GameBoyColorPlatform
from fsgamesys.platforms.gamegear import GameGearPlatform
from fsgamesys.platforms.lynx import LynxPlatformHandler
from fsgamesys.platforms.mastersystem import MasterSystemPlatform
from fsgamesys.platforms.megadrive import MegaDrivePlatform
from fsgamesys.platforms.msx import MsxPlatformHandler
from fsgamesys.platforms.nintendo64 import Nintendo64Platform
from fsgamesys.platforms.nintendods import NintendoDSPlatform
from fsgamesys.platforms.neogeo import NeoGeoPlatform
from fsgamesys.platforms.gamecube import GameCubePlatform
from fsgamesys.platforms.nintendo import NintendoPlatform
from fsgamesys.platforms.playstation import PlayStationPlatform
from fsgamesys.platforms.supernintendo import SuperNintendoPlatformHandler
from fsgamesys.platforms.turbografx16 import TurboGrafx16Platform
from fsgamesys.platforms.turbografxcd import TurboGrafxCDPlatform
# from fsgamesys.platforms.zxspectrum import SpectrumPlatform
from fsgamesys.platforms.spectrum import SpectrumPlatform


class UnsupportedPlatform(PlatformHandler):
    PLATFORM_NAME = "Unsupported"


platforms = {
    Platform.AMIGA: AmigaPlatformHandler,
    Platform.ARCADE: ArcadePlatformHandler,
    Platform.A2600: Atari2600PlatformHandler,
    Platform.A5200: Atari5200PlatformHandler,
    Platform.A7800: Atari7800PlatformHandler,
    "atari": AtariSTPlatform,  # FIXME: Deprecated
    Platform.C64: Commodore64Platform,
    Platform.CD32: CD32PlatformHandler,
    Platform.CDTV: CDTVPlatformHandler,
    Platform.CPC: CpcPlatform,
    Platform.DOS: DOSPlatformHandler,
    Platform.GB: GameBoyPlatform,
    Platform.GBA: GameBoyAdvancePlatform,
    Platform.GBC: GameBoyColorPlatform,
    Platform.LYNX: LynxPlatformHandler,
    Platform.MSX: MsxPlatformHandler,
    Platform.N64: Nintendo64Platform,
    Platform.NDS: NintendoDSPlatform,
    Platform.NEOGEO: NeoGeoPlatform,
    Platform.NES: NintendoPlatform,
    Platform.NGC: GameCubePlatform,
    Platform.PSX: PlayStationPlatform,
    Platform.SGG: GameGearPlatform,
    Platform.SMD: MegaDrivePlatform,
    Platform.SMS: MasterSystemPlatform,
    Platform.SNES: SuperNintendoPlatformHandler,
    Platform.SPECTRUM: SpectrumPlatform,
    Platform.ST: AtariSTPlatform,
    Platform.TG16: TurboGrafx16Platform,
    Platform.TGCD: TurboGrafxCDPlatform,
    Platform.ZXS: SpectrumPlatform,  # FIXME: Deprecated
}
PLATFORM_IDS = platforms.keys()


def normalize_platform_id(platform_id):
    platform_id = platform_id.lower().replace("-", "").replace("_", "")
    # noinspection SpellCheckingInspection
    if platform_id in ["commodorecdtv"]:
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
    elif platform_id in ["nintendods"]:
        return Platform.NDS
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
    if platform_id in ["st", "atarist"]:
        return Platform.ST
    elif platform_id in ["turbografx16"]:
        return Platform.TG16
    elif platform_id in ["gamegear", "sgg"]:
        return Platform.SGG
    return platform_id
