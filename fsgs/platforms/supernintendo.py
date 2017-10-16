import hashlib
import os

from fsgs import Option
from fsgs.drivers.mednafendriver import MednafenDriver
from fsgs.platform import PlatformHandler
from fsgs.platforms.loader import SimpleLoader


class SuperNintendoPlatformHandler(PlatformHandler):
    PLATFORM_NAME = "Super Nintendo"

    def __init__(self):
        PlatformHandler.__init__(self)

    def get_loader(self, fsgs):
        return SuperNintendoLoader(fsgs)

    def get_runner(self, fsgs):
        return SuperNintendoMednafenDriver(fsgs)


class SuperNintendoLoader(SimpleLoader):
    pass


SNES_CONTROLLER = {
    "type": "gamepad",
    "description": "Gamepad",
    "mapping_name": "supernintendo",
}
SNES_PORTS = [
    {
        "description": "Port 1",
        "types": [SNES_CONTROLLER],
        "type_option": "snes_port_1_type",
        "device_option": "snes_port_1",
    }, {
        "description": "Port 2",
        "types": [SNES_CONTROLLER],
        "type_option": "snes_port_2_type",
        "device_option": "snes_port_2",
    },
]


class SuperNintendoMednafenDriver(MednafenDriver):
    PORTS = SNES_PORTS

    def __init__(self, fsgc):
        super().__init__(fsgc)
        self.helper = SuperNintendoHelper(self.options)

    def prepare(self):
        print("[DRIVER] Mednafen SNES driver preparing...")
        super().prepare()
        self.set_mednafen_aspect(4, 3)
        # We do aspect calculation separately. Must not be done twice.
        self.emulator.args.extend(["-snes.correct_aspect", "0"])
        # FIXME: Input ports configuration
        # FIXME: SNES model
        self.emulator.args.append(self.helper.prepare_rom(self))

    # def mednafen_aspect_ratio(self):
    #     return 4.0 / 3.0

    def mednafen_input_mapping(self, port):
        n = port + 1
        return {
            "A": "snes.input.port{}.gamepad.a".format(n),
            "B": "snes.input.port{}.gamepad.b".format(n),
            "X": "snes.input.port{}.gamepad.x".format(n),
            "Y": "snes.input.port{}.gamepad.y".format(n),
            "L": "snes.input.port{}.gamepad.l".format(n),
            "R": "snes.input.port{}.gamepad.r".format(n),
            "UP": "snes.input.port{}.gamepad.up".format(n),
            "DOWN": "snes.input.port{}.gamepad.down".format(n),
            "LEFT": "snes.input.port{}.gamepad.left".format(n),
            "RIGHT": "snes.input.port{}.gamepad.right".format(n),
            "SELECT": "snes.input.port{}.gamepad.select".format(n),
            "START": "snes.input.port{}.gamepad.start".format(n),
        }

    def mednafen_system_prefix(self):
        return "snes"

    def game_video_par(self):
        # These may not be entirely correct...
        # if self.is_pal():
        #     return (4 / 3) / (256 / 239)
        # else:
        #     return (4 / 3) / (256 / 224)
        size = self.game_video_size()
        return (4 / 3) / (size[0] / size[1])

    def game_video_size(self):
        if self.is_pal():
            size = (256, 239)
        else:
            size = (256, 224)
        return size

    def get_game_file(self, config_key="cartridge_slot"):
        return None


class SuperNintendoHelper:
    def __init__(self, options):
        self.options = options

    def prepare_rom(self, driver):
        file_uri = self.options[Option.CARTRIDGE_SLOT]
        input_stream = driver.fsgc.file.open(file_uri)
        _, ext = os.path.splitext(file_uri)
        return self.prepare_rom_with_stream(driver, input_stream, ext)

    def prepare_rom_with_stream(self, driver, input_stream, ext):
        sha1_obj = hashlib.sha1()
        path = driver.temp_file("rom" + ext).path
        with open(path, "wb") as f:
            while True:
                data = input_stream.read(65536)
                if not data:
                    break
                f.write(data)
                sha1_obj.update(data)
        new_path = os.path.join(
            os.path.dirname(path), sha1_obj.hexdigest()[:8].upper() + ext)
        os.rename(path, new_path)
        return new_path
