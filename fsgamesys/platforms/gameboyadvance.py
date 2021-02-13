import hashlib
import os

from fsgamesys import Option
from fsgamesys.drivers.mednafendriver import MednafenDriver
from fsgamesys.platforms.loader import SimpleLoader
from fsgamesys.platforms.platform import Platform

# FIXME: Use KnownFile
# [BIOS] Game Boy Advance (World).gba
GBA_WORLD_BIOS_SHA1 = "300c20df6731a33952ded8c436f7f186d25d3492"

GBA_CONTROLLER = {
    "type": "gamepad",
    "description": "Built-in Controller",
    "mapping_name": "gameboyadvance",
}
GBA_PORTS = [
    {
        "description": "Built-in",
        "types": [GBA_CONTROLLER],
        "type_option": "gba_port_1_type",
        "device_option": "gba_port_1",
    }
]


class GameBoyAdvancePlatform(Platform):
    PLATFORM_NAME = "Game Boy Advance"

    def driver(self, fsgc):
        return GameBoyAdvanceMednafenDriver(fsgc)

    def loader(self, fsgc):
        return GameBoyAdvanceLoader(fsgc)


class GameBoyAdvanceLoader(SimpleLoader):
    def load_extra(self, values):
        self.config[Option.SRAM_TYPE] = values["sram_type"]


class GameBoyAdvanceMednafenDriver(MednafenDriver):
    PORTS = GBA_PORTS

    def __init__(self, fsgc):
        super().__init__(fsgc)
        self.helper = GameBoyAdvanceHelper(self.options)
        self.sram_type_file = None

    def prepare(self):
        print("[GBA] Mednafen GBA driver preparing...")
        super().prepare()
        self.set_mednafen_aspect(3, 2)
        # We do aspect calculation separately. Must not be done twice.
        # self.emulator.args.extend(["-snes.correct_aspect", "0"])
        # FIXME: Input ports configuration
        # FIXME: SNES model
        rom_path = self.helper.prepare_rom(self)
        self.emulator.args.append(rom_path)

        self.configure_gba_sram(rom_path)
        self.configure_gba_colormap()
        self.configure_gba_bios()

        print("[FIXME: temporarily removed support for custom sav file")
        # sav_file = os.path.splitext(rom_file)[0] + u".sav"
        # if os.path.exists(sav_file):
        #     m = hashlib.md5()
        #     with open(rom_file, "rb") as f:
        #         while True:
        #             data = f.read(16384)
        #             if not data:
        #                 break
        #             m.update(data)
        #         md5sum = str(m.hexdigest())
        #     save_name = os.path.splitext(
        #         os.path.basename(rom_file))[0] + u"." + md5sum + u".sav"
        #     dest_path = os.path.join(self.get_state_dir(), save_name)
        #     if not os.path.exists(dest_path):
        #         shutil.copy(sav_file, dest_path)

    # def init_input(self):
    #     # self.inputs = [
    #     #     self.create_input(name="Controller",
    #     #             type="gameboyadvance",
    #     #             description="Built-in Gamepad"),
    #     # ]
    #     self.set_mednafen_input_order()

    def finish(self):
        if self.sram_type_file:
            try:
                os.remove(self.sram_type_file)
            except Exception:
                # Not expected to happen, but is not critical if it does.
                print("[GBA] Could not remove SRAM type file")
        super().finish()

    def get_game_refresh_rate(self):
        # all GBA games should use a refresh rate of approx. 60.0 Hz
        # (or 30.0 Hz)
        return 59.73

    def mednafen_input_mapping(self, _):
        return {
            "A": "gba.input.builtin.gamepad.a",
            "B": "gba.input.builtin.gamepad.b",
            "L": "gba.input.builtin.gamepad.shoulder_l",
            "R": "gba.input.builtin.gamepad.shoulder_r",
            "UP": "gba.input.builtin.gamepad.up",
            "DOWN": "gba.input.builtin.gamepad.down",
            "LEFT": "gba.input.builtin.gamepad.left",
            "RIGHT": "gba.input.builtin.gamepad.right",
            "SELECT": "gba.input.builtin.gamepad.select",
            "START": "gba.input.builtin.gamepad.start",
        }

    def mednafen_rom_extensions(self):
        return [".gba"]

    def mednafen_scanlines_setting(self):
        return 33

    def mednafen_special_filter(self):
        return "nn2x"

    def mednafen_system_prefix(self):
        return "gba"

    def game_video_par(self):
        return 1.0

    def game_video_size(self):
        return 240, 160

    def configure_gba_sram(self, rom_path):
        if self.options[Option.SRAM_TYPE]:
            save_dir = self.save_handler.save_dir()
            rom_name = os.path.splitext(os.path.basename(rom_path))[0]
            type_file = os.path.join(save_dir, rom_name + ".type")
            with open(type_file, "wb") as f:
                for line in self.options[Option.SRAM_TYPE].split(";"):
                    f.write((line.strip() + "\n").encode("UTF-8"))
            self.sram_type_file = type_file

    def configure_gba_colormap(self):
        gamma = 1.3
        if self.options[Option.GBA_GAMMA]:
            try:
                gamma = float(self.options[Option.GBA_GAMMA])
            except ValueError:
                print("[GBA] WARNING: Invalid gamma value")
        self.create_colormap(os.path.join(self.home.path, "gba.pal"), gamma)
        # if os.path.exists(os.path.join(self.home.path, "gba.pal")):
        #     os.remove(os.path.join(self.home.path, "gba.pal"))
        # self.colormap_temp = self.temp_file("color.map")
        # self.create_colormap(self.colormap_temp.path, gamma)
        # self.emulator.args.extend(
        #     ["-gba.colormap", self.colormap_temp.path])

    def configure_gba_bios(self):
        uri = self.fsgc.file.find_by_sha1(GBA_WORLD_BIOS_SHA1)
        stream = self.fsgc.file.open(uri)
        if stream is not None:
            bios_temp = self.temp_file("gba_bios.bin")
            with open(bios_temp.path, "wb") as f:
                f.write(stream.read())
            self.emulator.args.extend(["-gba.bios", bios_temp.path])
        else:
            print("[GBA] WARNING: GBA BIOS not found, using HLE")

    @staticmethod
    def create_colormap(path, gamma):
        with open(path, "wb") as f:
            for x in range(32768):
                r = (x & 0x1F) << 3
                g = ((x & 0x3E0) >> 5) << 3
                b = ((x & 0x7C00) >> 10) << 3
                r /= 255.0
                g /= 255.0
                b /= 255.0
                # h, l, s = colorsys.rgb_to_hls(r, g, b)
                # l = l ** gamma
                # r, g, b = colorsys.hls_to_rgb(h, l, s)
                r = r ** gamma
                g = g ** gamma
                b = b ** gamma
                f.write(bytes([int(r * 255)]))
                f.write(bytes([int(g * 255)]))
                f.write(bytes([int(b * 255)]))

    def get_game_file(self, config_key="cartridge_slot"):
        return None


class GameBoyAdvanceHelper:
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
            os.path.dirname(path), sha1_obj.hexdigest()[:8].upper() + ext
        )
        os.rename(path, new_path)
        return new_path
