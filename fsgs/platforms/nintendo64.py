import os

from fsgs.drivers.retroarchdriver import RetroArchDriver
from fsgs.platform import Platform
from fsgs.platforms.loader import SimpleLoader
from fsgs.drivers.gamedriver import GameDriver, Emulator
from fsgs.input.mapper import InputMapper

N64_PLATFORM_ID = "n64"
N64_PLATFORM_NAME = "Nintendo 64"
N64_CONTROLLER = {
    "type": "gamepad",
    "description": "Gamepad",
    "mapping_name": "nintendo64",
}
N64_PORTS = [
    {"description": "Input Port 1", "types": [N64_CONTROLLER]},
    {"description": "Input Port 2", "types": [N64_CONTROLLER]},
    {"description": "Input Port 3", "types": [N64_CONTROLLER]},
    {"description": "Input Port 4", "types": [N64_CONTROLLER]},
]


class Nintendo64Platform(Platform):
    # FIXME: Move to init instead
    PLATFORM_NAME = N64_PLATFORM_NAME

    def driver(self, fsgs):
        return Nintendo64RetroArchDriver(fsgs)

    def loader(self, fsgs):
        return Nintendo64Loader(fsgs)


class Nintendo64Loader(SimpleLoader):
    pass


class Nintendo64MupenDriver(GameDriver):
    PORTS = [
        {"description": "Input Port 1", "types": [N64_CONTROLLER]},
        {"description": "Input Port 2", "types": [N64_CONTROLLER]},
        {"description": "Input Port 3", "types": [N64_CONTROLLER]},
        {"description": "Input Port 4", "types": [N64_CONTROLLER]},
    ]

    def __init__(self, fsgs):
        super().__init__(fsgs)
        self.emulator = Emulator("mupen64plus")
        self.emulator.allow_system_emulator = True
        self.helper = Nintendo64Helper(self.options)

    # def force_aspect_ratio(self):
    #     return 4.0 / 3.0

    # def game_video_size(self):
    #     # FIXME
    #     if self.is_pal():
    #         size = (256, 240)
    #     else:
    #         size = (256, 224)
    #     return size

    # FIXME: Scan/index byteswapped .n64/.z64 files? (i.e. #/original
    # and #!/byte-swapped.

    def prepare(self):
        temp_dir = self.temp_dir("mupen64plus")
        self.emulator.args.extend(["--configdir", temp_dir.path])
        self.emulator.args.extend(["--datadir", temp_dir.path])
        config_file = os.path.join(temp_dir.path, "mupen64plus.cfg")
        with open(config_file, "w") as f:
            self.write_config(f)
        input_config_file = os.path.join(temp_dir.path, "InputAutoCfg.ini")
        with open(input_config_file, "wb") as f:
            pass
        rom_path = self.get_game_file()
        self.emulator.args.extend([rom_path])

    def finish(self):
        pass

    # def run(self):
    #     plugin = pyapp.plug.get_plugin("no.fengestad.emulator.mupen64plus")
    #     if fs.windows:
    #         temp_dir = self.context.temp.dir("mupen64plus")
    #         GameCenterUtil.copy_folder_tree(plugin.get_bin_dir(), temp_dir)
    #         args = self.args[:]
    #         args.insert(0, os.path.join(temp_dir,
    #                     "mupen64plus-ui-console.exe"))
    #         return subprocess.Popen(args, env=self.env, cwd=temp_dir,
    #                 close_fds=True)
    #     return plugin.mupen64plus(self.args, env=self.env,
    #             cwd=plugin.get_bin_dir(), close_fds=True)

    def write_config(self, f):
        f.write("[Core]\n")
        f.write("OnScreenDisplay = False\n")
        # FIXME: Save state path does not seem to work
        # -stuff are saved to default dir in AppData/Roaming/Mupen64Plus/save
        # instead...
        # FIXME: Might work now with updated mupen64plus
        f.write(
            "SaveStatePath = '{path}'\n".format(
                path=self.get_state_dir() + os.sep
            )
        )
        self.configure_audio(f)
        self.configure_input(f)
        self.configure_video(f)

    def configure_audio(self, f):
        pass

    def configure_input(self, f):
        input_mapping = {
            "DPAD_RIGHT": "DPad R",
            "DPAD_LEFT": "DPad L",
            "DPAD_DOWN": "DPad D",
            "DPAD_UP": "DPad U",
            "START": "Start",
            "Z": "Z Trig",
            "B": "B Button",
            "A": "A Button",
            "C_RIGHT": "C Button R",
            "C_LEFT": "C Button L",
            "C_DOWN": "C Button D",
            "C_UP": "C Button U",
            "R": "R Trig",
            "L": "L Trig",
            "MEMPAK": "Mempak switch",
            "RUMBLEPAK": "Rumblepak switch",
            "STICK_LEFT": ("X Axis", 0),
            "STICK_RIGHT": ("X Axis", 1),
            "STICK_UP": ("Y Axis", 0),
            "STICK_DOWN": ("Y Axis", 1),
        }
        for i, port in enumerate(self.ports):
            if port.device is None:
                continue
            mapper = Mupen64PlusInputMapper(port, input_mapping)
            config = {}
            for key, value in mapper.items():
                print("---->", key, value)
                if isinstance(key, tuple):
                    key, index = key
                else:
                    index = 0
                config.setdefault(key, {})[index] = value
            f.write("\n[Input-SDL-Control{0}]\n\n".format(i + 1))
            f.write("version = 2\n")
            # Specifies whether this controller is 'plugged in' to the
            # simulated N64.
            f.write("plugged = True\n")
            # Specifies which type of expansion pak is in the controller:
            # 1=None, 2=Mem pak, 5=Rumble pak.
            f.write("plugin = 2\n")
            # If True, then mouse buttons may be used with this controller.
            f.write("mouse = False\n")
            # Controller configuration mode:
            # 0=Fully Manual, 1=Auto with named SDL Device, 2=Fully automatic.
            f.write("mode = 0\n")
            if port.device.type == "joystick":
                f.write("device = {0}\n".format(port.device.index))
                f.write('AnalogDeadZone = "512,512"\n')
                f.write('AnalogPeak = "32767,32767"\n')
            else:
                # -2 means keyboard/mouse
                f.write("device = -2\n")

            for key, value in config.items():
                type = value[0][0]
                values = [x[1][1] for x in sorted(list(value.items()))]
                values_str = ",".join(values)
                f.write(
                    '{key} = "{type}({values})"\n'.format(
                        key=key, type=type, values=values_str
                    )
                )
                print(
                    '{key} = "{type}({values})"\n'.format(
                        key=key, type=type, values=values_str
                    )
                )

    def configure_video(self, f):
        f.write("[Video-General]\n")
        if self.use_fullscreen():
            f.write("Fullscreen = True\n")
            f.write("ScreenWidth = {0}\n".format(self.screen_size()[0]))
            f.write("ScreenHeight = {0}\n".format(self.screen_size()[1]))
        else:
            f.write("Fullscreen = False\n")
            # f.write("ScreenWidth = 320\n")
            # f.write("ScreenHeight = 240\n")

        f.write("\n[UI-Console]\n\n")
        f.write("Version = 1\n")
        video_plugin = "glide64mk2"
        # video_plugin = "glide64"
        video_plugin = "rice"
        f.write('VideoPlugin = "mupen64plus-video-{}"\n'.format(video_plugin))

        if self.configure_vsync():
            # cannot find config for vsync in rice video plugin,
            # but should work for linux/nvidia due to env. variable
            # being set
            pass

        if video_plugin == "rice":
            self.configure_video_rice(f)
        elif video_plugin == "glide64":
            self.configure_video_glide64(f)
        elif video_plugin == "glide64mk2":
            self.configure_video_glide64mk2(f)

    def configure_video_rice(self, f):
        f.write("\n[Video-Rice]\n\n")
        f.write("AccurateTextureMapping = True\n")
        f.write("ForceAlphaBlender = True\n")
        # f.write("InN64Resolution = True\n")
        # f.write("RenderToTexture = 4\n")
        f.write("ScreenUpdateSetting = 2\n")
        # f.write("TextureFilteringMethod = 0\n")
        # f.write("Mipmapping = 1\n")
        # f.write("MultiSampling = 2\n")
        # f.write("AccurateTextureMapping = False\n")
        # f.write("WinFrameMode = True\n")
        # f.write("InN64Resolution = False\n")
        # f.write("ForceTextureFilter = 0\n")
        # f.write("TextureFilteringMethod = 1\n")
        # f.write("TextureFilteringMethod = 0\n")
        # f.write("FogMethod = 1\n")
        # f.write("EnableVertexShader = True\n")
        # f.write("NormalAlphaBlender = True\n")
        # f.write("ShowFPS = True\n")
        # f.write("EnableMipmaping = False\n")

        # self.args.extend(["--set", "Video-Rice[InN64resolution]=True"])
        # self.args.extend(["--set", "Video-Rice[ForceTextureFilter]=0"])

    def configure_video_glide64(self, f):
        f.write("\n[Video-Glide64]\n\n")

    def configure_video_glide64mk2(self, f):
        f.write("\n[Video-Glide64mk2]\n\n")
        # f.write("wrpResolution = 320x200\n")
        # f.write("filtering = 0\n")


class Mupen64PlusInputMapper(InputMapper):
    def axis(self, axis, positive):
        dir_str = "+" if positive else "-"
        return "axis", "{0}{1}".format(axis, dir_str)

    def hat(self, hat, direction):
        dir_str = {
            "left": "Left",
            "right": "Right",
            "up": "Up",
            "down": "Down",
        }[direction]
        return "hat", "{0} {1}".format(hat, dir_str)

    def button(self, button):
        return "button", str(button)

    def key(self, key):
        return "key", str(key.sdl_code)


class Nintendo64RetroDriver(GameDriver):
    PORTS = N64_PORTS

    def __init__(self, fsgs):
        super().__init__(fsgs)
        self.emulator = Emulator("retroarch")
        self.emulator.allow_system_emulator = True
        self.helper = Nintendo64Helper(self.options)

    def prepare(self):
        temp_dir = self.temp_dir("mupen64plus")
        self.emulator.args.extend(["--configdir", temp_dir.path])
        self.emulator.args.extend(["--datadir", temp_dir.path])
        config_file = os.path.join(temp_dir.path, "mupen64plus.cfg")
        with open(config_file, "w") as f:
            self.write_config(f)
        input_config_file = os.path.join(temp_dir.path, "InputAutoCfg.ini")
        with open(input_config_file, "wb") as f:
            pass
        rom_path = self.get_game_file()
        self.emulator.args.extend([rom_path])

    def finish(self):
        pass


class Nintendo64RetroArchDriver(RetroArchDriver):
    PORTS = N64_PORTS

    def __init__(self, fsgc):
        super().__init__(fsgc, "mupen64plus_libretro", "RetroArch/Mupen64Plus")
        self.helper = Nintendo64Helper(self.options)

    def prepare(self):
        super().prepare()
        rom_path = self.get_game_file()
        # self.helper.fix_ines_rom(rom_path)
        self.emulator.args.extend([rom_path])

        # Workaround for Intel / MESA on Linux (FIXME: Should perhaps check if
        # Intel / MESA driver is in use first...
        # https://github.com/gonetz/GLideN64/issues/454
        self.emulator.env["MESA_GL_VERSION_OVERRIDE"] = "3.3COMPAT"
        self.emulator.env["MESA_GLSL_VERSION_OVERRIDE"] = "420"

    def retroarch_input_mapping(self, port):
        input_mapping = {
            "A": "input_player{n}_b",
            "B": "input_player{n}_y",
            "DPAD_UP": "input_player{n}_up",
            "DPAD_DOWN": "input_player{n}_down",
            "DPAD_LEFT": "input_player{n}_left",
            "DPAD_RIGHT": "input_player{n}_right",
            "STICK_UP": "input_player{n}_l_y_minus",
            "STICK_DOWN": "input_player{n}_l_y_plus",
            "STICK_LEFT": "input_player{n}_l_x_minus",
            "STICK_RIGHT": "input_player{n}_l_x_plus",
            "C_UP": "input_player{n}_r_y_plus",
            "C_DOWN": "input_player{n}_r_y_minus",
            "C_LEFT": "input_player{n}_r_x_minus",
            "C_RIGHT": "input_player{n}_r_x_plus",
            "RUMBLEPAK": "input_player{n}_select",  # ???
            "START": "input_player{n}_start",
            "L": "input_player{n}_l",
            "R": "input_player{n}_r",
            "Z": "input_player{n}_l2",
        }
        return {k: v.format(n=port + 1) for k, v in input_mapping.items()}


class Nintendo64Helper:
    def __init__(self, options):
        self.options = options
