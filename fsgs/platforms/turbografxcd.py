from fsgs.knownfiles import KnownFile
from fsgs.platform import Platform
from fsgs.platforms.loader import CDPlatformLoader
from fsgs.platforms.turbografx16 import TurboGrafx16MednafenDriver

TGCD_PLATFORM_ID = "tgcd"
TGCD_PLATFORM_NAME = "TurboGrafx-CD"
TGCD_CONTROLLER = {
    "type": "gamepad",
    "description": "Gamepad",
    "mapping_name": "turbografx16",
}
SYSCARD3_PCE = KnownFile(
    "1b4c260326d905bc718812dad0f68089977f427b",
    TGCD_PLATFORM_ID,
    "syscard3.pce",
)


class TurboGrafxCDPlatform(Platform):
    PLATFORM_ID = TGCD_PLATFORM_ID
    PLATFORM_NAME = TGCD_PLATFORM_NAME

    def __init__(self):
        super().__init__()

    def driver(self, fsgc):
        return TurboGrafxCDMednafenDriver(fsgc)

    def loader(self, fsgc):
        return TurboGrafxCDLoader(fsgc)


class TurboGrafxCDLoader(CDPlatformLoader):
    pass


class TurboGrafxCDMednafenDriver(TurboGrafx16MednafenDriver):
    PORTS = [
        {"description": "Input Port 1", "types": [TGCD_CONTROLLER]},
        {"description": "Input Port 2", "types": [TGCD_CONTROLLER]},
    ]

    def __init__(self, fsgc):
        super().__init__(fsgc)

    # def game_video_par(self):
    #     return (4 / 3) / (288 / 232)
    #
    # def game_video_size(self):
    #     return 288 * 2, 232 * 2

    def mednafen_system_prefix(self):
        return "pce"

    def prepare(self):
        # self.emulator.args.extend(
        #     ["-pce.enable", "0", "-pce_fast.enable", "0"])
        # self.emulator.args.extend(["-force_module", "pce_fast"])
        # self.emulator.args.extend(["-force_module", "pce"])
        super().prepare()
        self.prepare_mednafen_bios(SYSCARD3_PCE, "syscard3.pce")
        self.prepare_mednafen_cd_images()

    def get_game_file(self, config_key="cartridge_slot"):
        return None
