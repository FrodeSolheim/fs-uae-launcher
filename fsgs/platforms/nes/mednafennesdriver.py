from binascii import unhexlify

from fsgs.drivers.mednafendriver import MednafenDriver


class MednafenNesDriver(MednafenDriver):

    CONTROLLER = {
        "type": "gamepad",
        "description": "Gamepad",
        "mapping_name": "nintendo",
    }

    PORTS = [
        {
            "description": "1st Controller",
            "types": [CONTROLLER]
        }, {
            "description": "2nd Controller",
            "types": [CONTROLLER]
        },
    ]

    def __init__(self, fsgs):
        super().__init__(fsgs)

    def force_aspect_ratio(self):
        return 4.0 / 3.0

    def mednafen_extra_graphics_options(self):
        options = []
        if self.is_pal():
            options.extend(["-nes.pal", "1"])
        else:
            options.extend(["-nes.pal", "0"])
        if self.nes_clip_sides():
            options.extend(["-nes.clipsides", "1"])
        return options

    def mednafen_input_mapping(self, port):
        if port == 0:
            return {
                "A": "nes.input.port1.gamepad.a",
                "B": "nes.input.port1.gamepad.b",
                "UP": "nes.input.port1.gamepad.up",
                "DOWN": "nes.input.port1.gamepad.down",
                "LEFT": "nes.input.port1.gamepad.left",
                "RIGHT": "nes.input.port1.gamepad.right",
                "SELECT": "nes.input.port1.gamepad.select",
                "START": "nes.input.port1.gamepad.start",
            }
        elif port == 1:
            return {
                "A": "nes.input.port2.gamepad.a",
                "B": "nes.input.port2.gamepad.b",
                "UP": "nes.input.port2.gamepad.up",
                "DOWN": "nes.input.port2.gamepad.down",
                "LEFT": "nes.input.port2.gamepad.left",
                "RIGHT": "nes.input.port2.gamepad.right",
                "SELECT": "nes.input.port2.gamepad.select",
                "START": "nes.input.port2.gamepad.start",
            }

    def mednafen_rom_extensions(self):
        return [".nes"]

    def mednafen_system_prefix(self):
        return "nes"

    def game_video_size(self):
        # FIXME
        if self.is_pal():
            size = (256, 240)
        else:
            size = (256, 224)
        if self.nes_clip_sides():
            size = (size[0] - 16, size[1])
        return size

    def nes_clip_sides(self):
        # FIXME: Sane default? -Or enable this in a per-game config
        # instead? SMB3 looks better with this
        return True

    def get_game_file(self, config_key="cartridge_slot"):
        path = super().get_game_file()
        data1 = b""
        with open(path, "rb") as f:

            # Start iNES Hack
            data = f.read(16)
            if len(data) == 16 and data.startswith(b"NES\x1a"):
                print("[DRIVER] Stripping iNES header")
            else:
                # No iNES header, include data
                data1 = data
            # End iNES Hack

            data2 = f.read()
        with open(path, "wb") as f:
            ines_header = self.config.get("ines_header", "")
            if ines_header:
                assert len(ines_header) == 32
                f.write(unhexlify(ines_header))
            f.write(data1)
            f.write(data2)
        return path
