import os

from fscore.system import System
from fsgamesys.drivers.gamedriver import GameDriver, Emulator
from fsgamesys.input.mapper import InputMapper


class DolphinDriver(GameDriver):
    def __init__(self, fsgs):
        super().__init__(fsgs)
        self.emulator = Emulator("dolphin-emu")
        self.emulator.allow_system_emulator = True

    def prepare(self):
        # configure dolphin.ini
        temp_dir = self.temp_dir("dolphin")
        dolphin_config_file = os.path.join(
            temp_dir.path, "user", "Config", "Dolphin.ini"
        )
        if not os.path.exists(os.path.dirname(dolphin_config_file)):
            os.makedirs(os.path.dirname(dolphin_config_file))

        with open(dolphin_config_file, "w", encoding="UTF-8") as f:
            self.configure(f)

        # media options
        rom_path = self.get_game_file()
        self.emulator.args.extend(["--exec=" + rom_path])

    def finish(self):
        pass

    def configure(self, f):
        temp_dir = self.temp_dir("dolphin")

        f.write("[Interface]\n")
        f.write("HideCursor = True\n")
        f.write("[Display]\n")
        f.write("RenderToMain = True\n")
        f.write(
            "FullscreenResolution = {w}x{h}\n".format(
                w=self.screen_size()[0], h=self.screen_size()[1]
            )
        )
        if self.use_fullscreen():
            f.write("Fullscreen = True\n")
        else:
            f.write("Fullscreen = False\n")

        f.write("[Core]\n")
        if System.windows:
            f.write("GFXPlugin = Plugin_VideoDX9.dll\n")

        # Force Interpreter (Cached) core.
        f.write("CPUCore = 0\n")

        self.dolphin_configure_core(f)
        self.dolphin_configure_input()

        # graphics options
        if self.use_vsync():
            vsync = True
        else:
            vsync = False
        if System.windows:
            graphics_config_file = os.path.join(
                temp_dir, "user", "Config", "gfx_dx9.ini"
            )
            with open(graphics_config_file, "w") as f:
                f.write("[Hardware]\n")
                if vsync:
                    f.write("VSync = True\n")
                else:
                    f.write("VSync = False\n")
                f.write("[Settings]\n")
                f.write("DisableFog = True\n")
                f.write("[Hacks]\n")
                f.write("EFBToTextureEnable = True\n")
        else:
            graphics_config_file = os.path.join(
                temp_dir.path, "user", "Config", "gfx_opengl.ini"
            )
            with open(graphics_config_file, "w") as f:
                f.write("[Hardware]\n")
                if vsync:
                    f.write("VSync = True\n")
                else:
                    f.write("VSync = False\n")
                f.write("[Settings]\n")

    def dolphin_configure_core(self, f):
        pass

    def dolphin_configure_input(self):
        pass


class DolphinInputMapper(InputMapper):
    def axis(self, axis, positive):
        dir_str = "+" if positive else "-"
        return "Axis " + str(axis) + dir_str

    def hat(self, hat, direction):
        dir_str = {"left": "W", "right": "E", "up": "N", "down": "S"}[
            direction
        ]
        return "Hat " + str(hat) + " " + dir_str

    def button(self, button):
        return "Button " + str(button)

    # Mouse values
    # elif value.startswith("M/"):
    #    if value == "M/UP": return "Cursor Y-"
    #    if value == "M/DOWN": return "Cursor Y+"
    #    if value == "M/LEFT": return "Cursor X-"
    #    if value == "M/RIGHT": return "Cursor X+"
    #    if value == "M/00": return "Click 0"
    #    if value == "M/01": return "Click 1"
    #    if value == "M/02": return "Click 2"
    #    raise Exception("unknown mouse value " + value)
    # else:
    #    #if fs.windows:
    #    #    return key_mapping[value]
    #    #else:
    #    #    return value
    #    return ""

    def key(self, key):
        if System.windows:
            return key.dinput_name[4:]
        else:
            return key.sdl_name[5:]

    def mouse(self, button, axis, positive):
        if button:
            return "Click " + str(button - 1)
        else:
            if axis == 0:
                return "Cursor X+" if positive else "Cursor X-"
            if axis == 1:
                return "Cursor Y+" if positive else "Cursor Y-"
