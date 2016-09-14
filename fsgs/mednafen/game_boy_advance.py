import os
import hashlib
from fsgs.mednafen.mednafen import MednafenRunner


# noinspection PyAttributeOutsideInit
class GameBoyAdvanceRunner(MednafenRunner):

    CONTROLLER = {
        "type": "gamepad",
        "description": "Built-in Controller",
        "mapping_name": "gameboyadvance",
    }

    PORTS = [
        {
            "description": "Controller",
            "types": [CONTROLLER]
        },
    ]

    def __init__(self, fsgs):
        super().__init__(fsgs)

    # def init_input(self):
    #     # self.inputs = [
    #     #     self.create_input(name="Controller",
    #     #             type="gameboyadvance",
    #     #             description="Built-in Gamepad"),
    #     # ]
    #     self.set_mednafen_input_order()

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

    def mednafen_post_configure(self):
        rom_file = self.get_game_file()
        cfg_file = os.path.splitext(rom_file)[0] + ".cfg"
        m = hashlib.md5()
        with open(rom_file, "rb") as f:
            while True:
                data = f.read(16384)
                if not data:
                    break
                m.update(data)
        rom_md5 = str(m.hexdigest())

        # save_name = os.path.splitext(
        #     os.path.basename(rom_file))[0] + u"." + md5sum + u".sav"

        if self.config["sram_type"]:
            state_dir = self.emulator_state_dir("mednafen")
            # type_file = os.path.join(
            #     state_dir,
            #     os.path.splitext(os.path.basename(rom_file))[0] + u".type")
            type_file = os.path.join(
                state_dir, rom_md5 + u".type")
            with open(type_file, "wb") as f:
                for line in self.config["sram_type"].split(";"):
                    f.write((line.strip() + "\n").encode("UTF-8"))

        print("FIXME: temporarily removed support for custom sav file")
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

        print("FIXME: temporarily removed supported for custom colormap")
        # self.colormap_temp = self.create_temp_file("color.map")
        # self.create_colormap(self.colormap_temp.path, 1.3)
        self.create_colormap(
            os.path.join(self.home.path, "gba.pal"), 1.3)
        # self.args.insert(0, self.colormap_temp.path)
        # self.args.insert(0, "-gba.colormap")

    def mednafen_rom_extensions(self):
        return [".gba"]

    def mednafen_scanlines_setting(self):
        return 33

    def mednafen_special_filter(self):
        return "nn2x"

    def mednafen_system_prefix(self):
        return "gba"

    # def mednafen_video_size(self):
    #     return 240, 160

    def create_colormap(self, path, gamma):
        with open(path, "wb") as f:
            for x in range(32768):
                r = (x & 0x1f) << 3
                g = ((x & 0x3e0) >> 5) << 3
                b = ((x & 0x7c00) >> 10) << 3

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
