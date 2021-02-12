from fsgamesys.drivers.mednafendriver import MednafenDriver
from fsgamesys.platforms.platform import Platform
from fsgamesys.platforms.loader import CartridgePlatformLoader

"""
Some information from https://en.wikipedia.org/wiki/TurboGrafx-16:

All PC Engine hardware outputs video in NTSC format, including the European
TurboGrafx; it generates a PAL-compatible video signal by using a chroma
encoder chip not found in any other system in the series.

X (Horizontal) Resolution: variable, maximum of 565 (programmable to 282,
377 or 565 pixels, or as 5.3693175 MHz, 7.15909 MHz, and 10.738635 MHz pixel
dot clock). Taking into consideration overscan limitations of CRT televisions
at the time, the horizontal resolutions were realistically limited to
something a bit less than what the system was actually capable of.
Consequently, most game developers limited their games to either 256, 352,
or 512 pixels in display width for each of the three modes.[23]

Y (Vertical) Resolution: variable, maximum of 242 (programmable in increments
of 1 scanline). It is possible to achieve an interlaced "mode" with a maximum
vertical resolution of 484 scanlines by alternating between the two different
vertical resolution modes used by the system. However, it is unknown, at this
time, if this interlaced resolution is compliant with (and hence displayed
correctly on) NTSC televisions.

The majority of TurboGrafx-16 games use 256×239
"""

TG16_CONTROLLER = {
    "type": "gamepad",
    "description": "Gamepad",
    "mapping_name": "turbografx16",
}


class TurboGrafx16Platform(Platform):
    PLATFORM_ID = "tg16"
    PLATFORM_NAME = "TurboGrafx-16"

    def __init__(self):
        super().__init__()

    def driver(self, fsgc):
        return TurboGrafx16MednafenDriver(fsgc)

    def loader(self, fsgc):
        return TurboGrafx16Loader(fsgc)


class TurboGrafx16Loader(CartridgePlatformLoader):
    pass


class TurboGrafx16MednafenDriver(MednafenDriver):
    PORTS = [
        {"description": "Input Port 1", "types": [TG16_CONTROLLER]},
        {"description": "Input Port 2", "types": [TG16_CONTROLLER]},
    ]

    def __init__(self, fsgc):
        super().__init__(fsgc)

    def game_video_par(self):
        size = self.game_video_size()
        return (4 / 3) / (size[0] / size[1])

    def game_video_size(self):
        # if self.is_pal():
        #     size = (256, 240)
        # else:
        #     size = (256, 240)
        size = (288, 232)
        return size

    def get_game_refresh_rate(self):
        return 59.94

    def mednafen_input_mapping(self, port):
        if port == 0:
            return {
                "1": "pce.input.port1.gamepad.i",
                "2": "pce.input.port1.gamepad.ii",
                "UP": "pce.input.port1.gamepad.up",
                "DOWN": "pce.input.port1.gamepad.down",
                "LEFT": "pce.input.port1.gamepad.left",
                "RIGHT": "pce.input.port1.gamepad.right",
                "SELECT": "pce.input.port1.gamepad.select",
                "RUN": "pce.input.port1.gamepad.run",
            }
        elif port == 1:
            return {
                "1": "pce.input.port2.gamepad.i",
                "2": "pce.input.port2.gamepad.ii",
                "UP": "pce.input.port2.gamepad.up",
                "DOWN": "pce.input.port2.gamepad.down",
                "LEFT": "pce.input.port2.gamepad.left",
                "RIGHT": "pce.input.port2.gamepad.right",
                "SELECT": "pce.input.port2.gamepad.select",
                "RUN": "pce.input.port2.gamepad.run",
            }

    def mednafen_system_prefix(self):
        return "pce"
