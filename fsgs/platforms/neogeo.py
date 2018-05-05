import json

from fsgs.drivers.mamedriver import MameDriver
from fsgs.option import Option
from fsgs.platform import Platform
from fsgs.platforms.arcade.arcadeplatform import ArcadeLoader

NEOGEO_PLATFORM_ID = "neogeo"
NEOGEO_PLATFORM_NAME = "Neo-Geo"
NEOGEO_MODEL_MVS = "mvs"
NEOGEO_MODEL_MVS_US = "mvs/us"
NEOGEO_MODEL_MVS_JP = "mvs/jp"
NEOGEO_MODEL_AES = "aes"
NEOGEO_MODEL_AES_JP = "aes/jp"
# noinspection SpellCheckingInspection
NEOGEO_ASIA_BIOS = {
    "neo-epo.bin": "1b3b22092f30c4d1b2c15f04d1670eb1e9fbea07"
}
# noinspection SpellCheckingInspection
NEOGEO_JAPAN_BIOS = {
    "neo-po.bin": "4e4a440cae46f3889d20234aebd7f8d5f522e22c"
}
NEOGEO_CONTROLLER = {
    "type": "gamepad",
    "description": "Gamepad",
    "mapping_name": "neogeo",
}


class NeoGeoPlatform(Platform):
    PLATFORM_ID = NEOGEO_PLATFORM_ID
    PLATFORM_NAME = NEOGEO_PLATFORM_NAME

    def __init__(self):
        super().__init__()

    def driver(self, fsgc):
        return NeoGeoDriver(fsgc)

    def loader(self, fsgc):
        return NeoGeoLoader(fsgc)


class NeoGeoLoader(ArcadeLoader):
    pass


class NeoGeoDriver(MameDriver):
    PORTS = [
        {
            "description": "Input Port 1",
            "types": [NEOGEO_CONTROLLER]
        }, {
            "description": "Input Port 2",
            "types": [NEOGEO_CONTROLLER]
        }
    ]

    def __init__(self, fsgc):
        super().__init__(fsgc)
        self.helper = NeoGeoHelper(self.options)

    def mame_input_mapping(self, _):
        if self.helper.aes():
            return {
                "START": "P#_START",
                "SELECT": "P#_SELECT",
                "UP": "P#_JOYSTICK_UP",
                "DOWN": "P#_JOYSTICK_DOWN",
                "LEFT": "P#_JOYSTICK_LEFT",
                "RIGHT": "P#_JOYSTICK_RIGHT",
                "A": "P#_BUTTON1",
                "B": "P#_BUTTON2",
                "C": "P#_BUTTON3",
                "D": "P#_BUTTON4",
            }
        else:
            return {
                "START": "START#",
                "SELECT": "COIN#",
                "UP": "P#_JOYSTICK_UP",
                "DOWN": "P#_JOYSTICK_DOWN",
                "LEFT": "P#_JOYSTICK_LEFT",
                "RIGHT": "P#_JOYSTICK_RIGHT",
                "A": "P#_BUTTON1",
                "B": "P#_BUTTON2",
                "C": "P#_BUTTON3",
                "D": "P#_BUTTON4",
            }

    def mame_romset(self):
        romset = {}
        for entry in json.loads(self.options["file_list"]):
            romset[entry["name"]] = entry["sha1"]

        if self.helper.model() == NEOGEO_MODEL_MVS:
            romset.update({
                "sp-s2.sp1": "4f5ed7105b7128794654ce82b51723e16e389543",
            })
        elif self.helper.model() == NEOGEO_MODEL_MVS_JP:
            # noinspection SpellCheckingInspection
            romset.update({
                "vs-bios.rom": "ecf01eda815909f1facec62abf3594eaa8d11075",
            })
        elif self.helper.model() == NEOGEO_MODEL_MVS_US:
            romset.update({
                "sp-u2.sp1": "5c6bba07d2ec8ac95776aa3511109f5e1e2e92eb",
            })
        elif self.helper.model() == NEOGEO_MODEL_AES:
            romset.update(NEOGEO_ASIA_BIOS)
        elif self.helper.model() == NEOGEO_MODEL_AES_JP:
            romset.update(NEOGEO_JAPAN_BIOS)

        if self.helper.aes():
            machine = "aes"
            # noinspection SpellCheckingInspection
            romset.update({
                "000-lo.lo": "5992277debadeb64d1c1c64b0a92d9293eaf7e4a",
            })
        else:
            machine = "neogeo"
            # noinspection SpellCheckingInspection
            romset.update({
                "000-lo.lo": "5992277debadeb64d1c1c64b0a92d9293eaf7e4a",
                "sfix.sfix": "fd4a618cdcdbf849374f0a50dd8efe9dbab706c3",
                "sm1.sm1": "42f9d7ddd6c0931fd64226a60dc73602b2819dcf",
            })

        return machine, romset

    def prepare(self):
        super().prepare()
        self.create_mame_layout()

        self.install_mame_hash_file("neogeo.xml")
        self.emulator.args.append(self.options["mame_rom_set"])
        if self.helper.model() == NEOGEO_MODEL_AES_JP:
            self.emulator.args.extend(["-bios", "japan"])
        elif self.helper.model() == NEOGEO_MODEL_MVS_JP:
            self.emulator.args.extend(["-bios", "japan"])
        elif self.helper.model() == NEOGEO_MODEL_MVS_US:
            self.emulator.args.extend(["-bios", "us"])


class NeoGeoHelper:
    def __init__(self, options):
        self.options = options

    def model(self):
        if self.options[Option.NEOGEO_MODEL] == NEOGEO_MODEL_AES:
            return NEOGEO_MODEL_AES
        if self.options[Option.NEOGEO_MODEL] == NEOGEO_MODEL_AES_JP:
            return NEOGEO_MODEL_AES_JP
        if self.options[Option.NEOGEO_MODEL] == NEOGEO_MODEL_MVS_US:
            return NEOGEO_MODEL_MVS_US
        if self.options[Option.NEOGEO_MODEL] == NEOGEO_MODEL_MVS_JP:
            return NEOGEO_MODEL_MVS_JP
        return NEOGEO_MODEL_MVS

    def aes(self):
        return self.model() in [NEOGEO_MODEL_AES, NEOGEO_MODEL_AES_JP]
