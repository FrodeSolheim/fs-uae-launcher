import hashlib
import os
from binascii import unhexlify

from fsgamesys import Option
from fsgamesys.drivers.messdriver import MessDriver
from fsgamesys.platforms.platform import Platform
from fsgamesys.platforms.loader import SimpleLoader

A7800_PLATFORM_ID = "a7800"
A7800_PLATFORM_NAME = "Atari 7800"
A7800_MODEL_NTSC = "ntsc"
A7800_MODEL_PAL = "pal"
A7800_JOYSTICK = {
    "type": "joystick",
    "description": "Joystick",
    "mapping_name": "atari7800",
}
NO_CONTROLLER_TYPE = "none"
NO_CONTROLLER = {
    "type": NO_CONTROLLER_TYPE,
    "description": "None",
    "mapping_name": "",
}
A7800_PORTS = [
    {
        "description": "Port 1",
        "types": [A7800_JOYSTICK, NO_CONTROLLER],
        "type_option": "a7800_port_1_type",
        "device_option": "a7800_port_1",
    },
    {
        "description": "Port 2",
        "types": [A7800_JOYSTICK, NO_CONTROLLER],
        "type_option": "a7800_port_2_type",
        "device_option": "a7800_port_2",
    },
]
# noinspection SpellCheckingInspection
A7800_ROMS = {
    "d9d134bb6b36907c615a594cc7688f7bfcef5b43": "7800.u7",
    "14584b1eafe9721804782d4b1ac3a4a7313e455f": "c300558-001a.u7",
}

# noinspection SpellCheckingInspection
A7800P_ROMS = {"5a140136a16d1d83e4ff32a19409ca376a8df874": "7800pal.rom"}


class Atari7800PlatformHandler(Platform):
    PLATFORM_NAME = A7800_PLATFORM_NAME

    def driver(self, fsgc):
        return Atari7800MameDriver(fsgc)

    def loader(self, fsgc):
        return Atari7800Loader(fsgc)


class Atari7800Loader(SimpleLoader):
    def load_extra(self, values):
        self.config[Option.A7800_MODEL] = values["a7800_model"]
        self.config[Option.A7800_A78_HEADER] = values["a78_header"]
        self.config[Option.A7800_PORT_1_TYPE] = values["a7800_port_1_type"]
        self.config[Option.A7800_PORT_2_TYPE] = values["a7800_port_2_type"]


class Atari7800MameDriver(MessDriver):
    PORTS = A7800_PORTS

    def __init__(self, fsgc):
        super().__init__(fsgc)
        self.helper = Atari7800Helper(self.options)

    def prepare(self):
        super().prepare()
        # self.emulator.args.extend(
        #     ["-lightgun", "-lightgun_device", "mouse"])

    def get_game_file(self, config_key="cartridge_slot"):
        return self.helper.prepare_rom(self)

    def mess_configure(self):
        self.mess_configure_cartridge()

    def mess_input_mapping(self, port):
        return {
            "START": "P#_START",
            "UP": "P#_JOYSTICK_UP",
            "DOWN": "P#_JOYSTICK_DOWN",
            "LEFT": "P#_JOYSTICK_LEFT",
            "RIGHT": "P#_JOYSTICK_RIGHT",
            "1": "P#_BUTTON1",
            "2": "P#_BUTTON2",
        }

    def mess_romset(self):
        if self.helper.model() == A7800_MODEL_PAL:
            return "a7800p", A7800P_ROMS
        else:
            return "a7800", A7800_ROMS


class Atari7800Helper:
    def __init__(self, options):
        self.options = options

    def model(self):
        model = self.options[Option.A7800_MODEL]
        if model in ["", A7800_MODEL_NTSC]:
            return A7800_MODEL_NTSC
        elif model == A7800_MODEL_PAL:
            return A7800_MODEL_PAL
        else:
            print("[A7800] Warning: Invalid model:", model)
            return A7800_MODEL_NTSC

    def pal(self):
        return self.model() == A7800_MODEL_PAL

    def prepare_rom(self, driver):
        file_uri = self.options[Option.CARTRIDGE_SLOT]
        input_stream = driver.fsgc.file.open(file_uri)
        _, ext = os.path.splitext(file_uri)
        return self.prepare_rom_with_stream(driver, input_stream, ext)

    def prepare_rom_with_stream(self, driver, input_stream, ext):
        # This should not be necessary for files found via the file database
        # and the online game database, but could be necessary for manually
        # loaded files.
        data = input_stream.read(128)
        if len(data) == 128 and data[1:10] == b"ATARI7800":
            print("[A7800] Stripping A78 header")
            data = None
        else:
            # No A78 header, include data
            pass
        sha1_obj = hashlib.sha1()
        path = driver.temp_file("rom" + ext).path
        with open(path, "wb") as f:
            header = self.options[Option.A7800_A78_HEADER]
            if header:
                assert len(header) == 128 * 2
                f.write(unhexlify(header))
                sha1_obj.update(unhexlify(header))
            if data is not None:
                f.write(data)
                sha1_obj.update(data)
            while True:
                data = input_stream.read(65536)
                if not data:
                    break
                f.write(data)
                sha1_obj.update(data)
        new_path = os.path.join(
            os.path.dirname(path), sha1_obj.hexdigest()[:8].upper() + ext
        )
        os.rename(path, new_path)
        return new_path
