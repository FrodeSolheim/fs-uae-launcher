import io
import os
import shutil
import tempfile
import warnings
from collections import defaultdict

import fsboot
from fsbc.application import Application
from fsbc.resources import Resources
from fsbc.settings import Settings
from fsbc.system import System
from fsbc.task import current_task
from fsgs.FSGSDirectories import FSGSDirectories
from fsgs.amiga.fsuae import FSUAE
from fsgs.option import Option
from fsgs.plugins.plugin_manager import PluginManager
from fsgs.refreshratetool import RefreshRateTool
from fsgs.util.gamenameutil import GameNameUtil


# noinspection PyMethodMayBeStatic
class GameDriver:
    PORTS = []

    def __init__(self, fsgc):
        self.fsgc = fsgc
        self.files = GameFiles(fsgc)
        self.emulator = GameEmulator()
        self._allow_gsync = True
        self._model_name = ""

        self.options = defaultdict(str)
        for key, value in Settings.instance().values.items():
            # FIXME: re-enable this check?
            # if key in Config.config_keys:
            #     print("... ignoring config key from settings:", key)
            #     continue
            self.options[key] = value
        for key, value in self.fsgc.config.items():
            self.options[key] = value

        self.ports = []
        for port_info in self.PORTS:
            port = Port(port_info["description"])
            port.types = port_info["types"]
            self.ports.append(port)

        self.__vsync = False
        self.__game_temp_file = None
        self.temp_root = TemporaryItem(
            root=None, prefix="fsgs-", suffix="tmp", directory=True)

        # # Default current working directory for the emulator.
        self.cwd = self.temp_dir("cwd")
        # # Fake home directory for the emulator.
        self.home = self.temp_dir("home")

        self.home._path = os.path.join(FSGSDirectories.get_cache_dir(), "Home")
        if not os.path.exists(self.home.path):
            os.makedirs(self.home.path)
        self.cwd._path = self.home._path
        # self.cwd._path = os.path.join(self.home._path, "cwd")
        # if not os.path.exists(self.cwd.path):
        #     os.makedirs(self.cwd.path)

        # Deprecated compatibility name
        self.args = self.emulator.args
        # Deprecated compatibility name
        self.config = self.options
        # Deprecated compatibility name
        self.env = self.emulator.env
        # Deprecated compatibility name
        self.fsgs = self.fsgc

    def __del__(self):
        print("GameDriver.__del__")

    def prepare(self):
        pass

    def install(self):
        self.files.install()

    def run(self):
        executable = PluginManager.instance().find_executable(
            self.emulator.name)
        if executable is None:
            # if self.emulator.allow_system_emulator:
            #     pass
            raise LookupError(
                "Could not find emulator " + repr(self.emulator.name))
        self.emulator.process = self.start_emulator(executable)

    def wait(self):
        return self.emulator.process.wait()

    def finish(self):
        pass

    def set_env(self, name, value):
        warnings.warn("set_env is deprecated", DeprecationWarning)
        self.env[name] = value

    def add_arg(self, *args):
        warnings.warn("add_arg is deprecated", DeprecationWarning)
        self.args.extend(args)

    # def set_emulator(self, emulator):
    #     self._emulator = emulator

    # self.inputs.append(self.create_input(
    #         name='Controller {0}'.format(i + 1),
    #         type='megadrive',
    #         description='Gamepad'))

    def set_allow_gsync(self, allow):
        self._allow_gsync = False

    def set_model_name(self, name):
        self._model_name = name

    def use_fullscreen(self):
        # FIXME: not a very nice hack to hard-code application name here...
        if Application.instance():
            if Application.instance().name == "fs-uae-arcade":
                return True
        if Settings.instance()["fullscreen"] == "0":
            return False
        return True

    def use_vsync(self):
        # if "--no-vsync" in sys.argv:
        #     return False
        # return True
        return self.options[Option.VIDEO_SYNC] in ["1", "auto"]

    def use_doubling(self):
        return True

    NO_SMOOTHING = "0"
    SMOOTHING = "1"
    NON_INTEGER_SMOOTHING = "auto"
    DEFAULT_SMOOTHING = NON_INTEGER_SMOOTHING

    def smoothing(self):
        if self.options[Option.SMOOTHING] == self.NO_SMOOTHING:
            return self.NO_SMOOTHING
        if self.options[Option.SMOOTHING] == self.SMOOTHING:
            return self.SMOOTHING
        if self.options[Option.SMOOTHING] == self.NON_INTEGER_SMOOTHING:
            return self.NON_INTEGER_SMOOTHING
        return self.DEFAULT_SMOOTHING

    NO_SCALING = "0"
    MAX_SCALING = "1"
    INTEGER_SCALING = "integer"
    DEFAULT_SCALING = MAX_SCALING

    def scaling(self):
        if self.options[Option.SCALE] == self.NO_SCALING:
            return self.NO_SCALING
        if self.options[Option.SCALE] == self.MAX_SCALING:
            return self.MAX_SCALING
        if self.options[Option.SCALE] == self.INTEGER_SCALING:
            return self.INTEGER_SCALING
        return self.DEFAULT_SCALING

    NO_STRETCHING = "0"
    STRETCH_FILL_SCREEN = "1"
    STRETCH_ASPECT = "aspect"
    DEFAULT_STRETCHING = STRETCH_ASPECT

    def stretching(self):
        if self.options[Option.STRETCH] == self.NO_STRETCHING:
            return self.NO_STRETCHING
        if self.options[Option.STRETCH] == self.STRETCH_FILL_SCREEN:
            return self.STRETCH_FILL_SCREEN
        if self.options[Option.STRETCH] == self.STRETCH_ASPECT:
            return self.STRETCH_ASPECT
        return self.DEFAULT_STRETCHING

    NO_BORDER = "0"
    SMALL_BORDER = "1"
    LARGE_BORDER = "large"
    DEFAULT_BORDER = SMALL_BORDER

    def border(self):
        if self.options[Option.BORDER] == self.NO_BORDER:
            return self.NO_BORDER
        if self.options[Option.BORDER] == self.SMALL_BORDER:
            return self.SMALL_BORDER
        if self.options[Option.BORDER] == self.LARGE_BORDER:
            return self.LARGE_BORDER
        return self.DEFAULT_BORDER

    NO_EFFECT = "0"
    CRT_EFFECT = "crt"
    HQ2X_EFFECT = "hq2x"
    SCALE2X_EFFECT = "scale2x"
    DEFAULT_EFFECT = NO_EFFECT

    def effect(self):
        if self.options[Option.EFFECT] == self.NO_EFFECT:
            return self.NO_EFFECT
        if self.options[Option.EFFECT] == self.CRT_EFFECT:
            return self.CRT_EFFECT
        if self.options[Option.EFFECT] == self.HQ2X_EFFECT:
            return self.HQ2X_EFFECT
        if self.options[Option.EFFECT] == self.SCALE2X_EFFECT:
            return self.SCALE2X_EFFECT
        return self.DEFAULT_EFFECT

    # FIXME: REMOVE
    def use_smoothing(self):
        return True

    # FIXME: REMOVE
    def use_stretching(self):
        if self.options[Option.KEEP_ASPECT] == "1":
            return
        # if "--no-stretch" in sys.argv:
        #     return False
        # if self.options[Option.KEEP_ASPECT] == "1":
        #     return
        # if Settings.instance()["stretch"] == "0":
        #     return False
        return True

    def use_auto_load(self):
        if self.options[Option.AUTO_LOAD] == "0":
            return False
        return True

    def use_turbo_load(self):
        if self.options[Option.TURBO_LOAD] == "0":
            return False
        return True

    def use_audio_frequency(self):
        if self.options[Option.AUDIO_FREQUENCY]:
            try:
                return int(Settings.instance()[Option.AUDIO_FREQUENCY])
            except ValueError:
                pass
        return 48000

    def screenshots_dir(self):
        return FSGSDirectories.screenshots_output_dir()

    def screenshots_base(self):
        return GameNameUtil.create_link_name(self.game_name())

    def screenshots_name(self):
        # FIXME: REMOVE?
        return GameNameUtil.create_fs_name(self.get_name())

    # def get_game_name(self):
    #     return self.options["game_name"]
    #
    # def get_variant_name(self):
    #     return self.options["variant_name"]

    def get_platform_name(self):
        # FIXME: UNUSED? REMOVE?
        p = self.options[Option.PLATFORM].lower()
        if p == "atari-7800":
            return "Atari 7800"
        if p == "amiga":
            return "Amiga"
        if p == "cdtv":
            return "CDTV"
        if p == "cd32":
            return "CD32"
        raise Exception("Unrecognized platform")

    def screen_size(self):
        rect = self.screen_rect()
        return rect[2], rect[3]

    @classmethod
    def _screens(cls):
        screens = []
        try:
            from fsui.qt import init_qt
            qapplication = init_qt()
            desktop = qapplication.desktop()
        except AttributeError:
            # no QApplication, probably not running via QT
            # FIXME: log warning
            pass
        else:
            for i in range(desktop.screenCount()):
                geometry = desktop.screenGeometry(i)
                screens.append([geometry.x(), i, geometry])
        return screens

    @classmethod
    def screen_refresh_rate_for_monitor(cls, monitor):
        try:
            from fsui.qt import init_qt
            qapplication = init_qt()
        except AttributeError:
            return 0
        else:
            for i, screen in enumerate(qapplication.screens()):
                print("Screen {0} refresh rate (Qt) = {1}".format(
                    i, screen.refreshRate()))
            index = cls.screen_index_for_monitor(monitor)
            screen = qapplication.screens()[index]

            if System.windows or System.macos:
                return int(round(screen.refreshRate()))

            refresh_rate_tool = RefreshRateTool()
            screens = refresh_rate_tool.screens_xrandr()
            rect = cls.screen_rect_for_monitor(monitor)
            # from pprint import pprint
            # pprint(screens)
            for screen in screens:
                print("Screen {} refresh rate (Xrandr) = {}".format(
                    screen, screens[screen]["refresh_rate"]))
            for screen in screens:
                if rect == screen:
                    return screens[screen]["refresh_rate"]
            return 0

    def screen_refresh_rate(self):
        monitor = self.options[Option.MONITOR]
        return self.screen_refresh_rate_for_monitor(monitor)

    @classmethod
    def screen_index_for_monitor(cls, monitor):
        rect = cls.screen_rect_for_monitor(monitor)
        for i, s in enumerate(cls._screens()):
            if rect == (s[2].x(), s[2].y(), s[2].width(), s[2].height()):
                return i
        raise Exception("Could not find screen at position {}".format(rect))

    def screen_index(self):
        monitor = self.options[Option.MONITOR]
        return self.screen_index_for_monitor(monitor)

    @classmethod
    def screen_rect_for_monitor(cls, monitor):
        screens = cls._screens()
        screens.sort()
        if monitor == "left":
            mon = 0
        elif monitor == "middle-right":
            mon = 2
        elif monitor == "right":
            mon = 3
        else:  # middle-left
            mon = 1
        display = round(mon / 3 * (len(screens) - 1))
        geometry = screens[display][2]
        return geometry.x(), geometry.y(), geometry.width(), geometry.height()

    def screen_rect(self):
        monitor = self.options[Option.MONITOR]
        return self.screen_rect_for_monitor(monitor)

    def game_name(self):
        if self.fsgc.game.name:
            return self.fsgc.game.name
        if self.options["game_name"]:
            return self.options["game_name"]
        if self.options[Option.CONFIG_NAME]:
            return self.options[Option.CONFIG_NAME]
        return "Unknown Game"

    def variant_name(self):
        if self.fsgc.game.variant.name:
            return self.fsgc.game.variant.name
        if self.options["variant_name"]:
            return self.options["variant_name"]
        return "Unknown Variant"

    def get_name(self):
        # return "{0} ({1}, {2})".format(
        #     self.get_game_name(), self.get_platform_name(),
        #     self.get_variant_name())
        return "{0} ({1}, {2})".format(
            self.fsgc.game.name, self.fsgc.game.platform.name,
            self.fsgc.game.variant.name)

    def save_dir(self, create=False):
        """Uses the new saves layout."""
        uuid = self.fsgc.game.variant.uuid
        if uuid:
            path = os.path.join(
                FSGSDirectories.saves_dir, "UUID", uuid[:3], uuid)
            if create and not os.path.exists(path):
                os.makedirs(path)
            return path
        # For now, return old save state dirs for non-UUID variants
        return self.get_state_dir()

    def get_state_dir(self):
        """This is the old deprecated save sate directory for games."""
        state_dir = os.path.join(
            FSGSDirectories.get_save_states_dir(),
            GameNameUtil.create_fs_name(self.get_name()))
        if not os.path.exists(state_dir):
            os.makedirs(state_dir)
        if self.fsgc.game.variant.uuid:
            uuid_file = os.path.join(state_dir, "uuid.txt")
            with io.open(uuid_file, "w", encoding="UTF-8") as f:
                f.write(self.fsgc.game.variant.uuid + "\n")
        # timestamp_file = os.path.join(state_dir, "timestamp.txt")
        # with open(timestamp_file, "wb") as f:
        #     f.write("\n")
        return state_dir

    def emulator_state_dir(self, emulator):
        assert emulator
        state_dir = os.path.join(self.get_state_dir(), emulator)
        if not os.path.exists(state_dir):
            os.makedirs(state_dir)
        return state_dir

    def get_game_file(self, config_key="cartridge_slot"):
        if self.__game_temp_file is not None:
            return self.__game_temp_file.path

        file_uri = self.options[config_key]
        # FIXME: create new API fsgc.file.path(file_uri), returns path
        # (and creates temp file if necessary)
        input_stream = self.fsgc.file.open(file_uri)

        # self.__game_temp_file = self.fsgc.temp_file(file_uri.split("/")[-1])
        self.__game_temp_file = TemporaryNamedItem(
            self.temp_root, file_uri.split("/")[-1])

        with open(self.__game_temp_file.path, "wb") as f:
            while True:
                data = input_stream.read(65536)
                if not data:
                    break
                f.write(data)
        return self.__game_temp_file.path

    def create_temp_dir(self, suffix):
        warnings.warn("create_temp_dir is deprecated", DeprecationWarning)
        return self.temp_dir(suffix)

    def create_temp_file(self, suffix):
        warnings.warn("create_temp_file is deprecated", DeprecationWarning)
        return self.temp_file(suffix)

    def temp_dir(self, name):
        return TemporaryNamedItem(
            root=self.temp_root, name=name, directory=True)

    def temp_file(self, name):
        return TemporaryNamedItem(
            root=self.temp_root, name=name, directory=False)

    def start_emulator_from_plugin_resource(
            self, provide_name, args=None, env_vars=None):
        resource = self.fsgc.plugins.find_executable(provide_name)
        if resource is None:
            raise Exception("Could not find emulator " + repr(provide_name))
        if env_vars is None:
            env_vars = os.environ.copy()
        # Set LD_LIBRARY_PATH for Linux plugins with bundled libraries
        # EDIT: No longer doing, can cause problems for OpenGL drivers.
        # Instead, use the standalone-linux.py script with rpath fixing.
        # env_vars["LD_LIBRARY_PATH"] = os.path.dirname(resource.path)
        return self.start_emulator("", args=args, env_vars=env_vars,
                                   executable=resource.path)

    def set_environment_path(self, env, key, value):
        """Supports exporting paths with MBCS encoding as well on Windows."""
        env[key] = value
        # if System.windows:
        #     env[key + "_MBCS"] = value.encode("mbcs")

    def update_environment(self, env):
        x, y, w, h = self.screen_rect()
        if env.get("FSGS_FULLSCREEN_RECT", ""):
            # Already specified externally, so we just use
            # the existing values...
            print("using existing fullscreen rect")
        else:
            env["FSGS_FULLSCREEN_RECT"] = "{0},{1},{2},{3}".format(x, y, w, h)

        if self.use_fullscreen():
            fullscreen_mode = self.options[Option.FULLSCREEN_MODE]
            if fullscreen_mode == "window":
                env["FSGS_FULLSCREEN_MODE"] = "1"
            elif fullscreen_mode == "fullscreen":
                env["FSGS_FULLSCREEN_MODE"] = "2"
            else:
                env["FSGS_FULLSCREEN_MODE"] = "3"

            for key in ["FSGS_GEOMETRY", "FSGS_WINDOW"]:
                if env.get(key, ""):
                    # Already specified externally, so we just use
                    # the existing values...
                    pass
                    print("using existing fullscreen window rect")
                else:
                    env[key] = "{0},{1},{2},{3}".format(x, y, w, h)
            print("fullscreen rect:", env.get("FSGS_GEOMETRY", ""))
            # SDL 1.2 multi-display support. Hopefully, SDL's display
            # enumeration is the same as QT's.
            env["SDL_VIDEO_FULLSCREEN_DISPLAY"] = str(self.screen_index())

            if fullscreen_mode == "window":
                print("using fullscreen window mode")
                # env["FSGS_FULLSCREEN"] = "window"
                env["FSGS_FULLSCREEN"] = "1"
            else:
                del env["FSGS_WINDOW"]
                if fullscreen_mode == "fullscreen":
                    print("using fullscreen (legacy) mode")
                    # env["FSGS_FULLSCREEN"] = "fullscreen"
                    env["FSGS_FULLSCREEN"] = "2"
                else:
                    print("using fullscreen desktop mode")
                    # env["FSGS_FULLSCREEN"] = "desktop"
                    env["FSGS_FULLSCREEN"] = "3"
        else:
            print("using window mode (no fullscreen)")
            env["FSGS_FULLSCREEN"] = "0"

        # if self.use_stretching():
        #     self.env["FSGS_STRETCH"] = "1"
        # else:
        #     self.env["FSGS_STRETCH"] = "0"

        if self.stretching() == self.STRETCH_FILL_SCREEN:
            self.env["FSGS_STRETCH"] = "1"
        elif self.stretching() == self.STRETCH_ASPECT:
            self.env["FSGS_STRETCH"] = "2"
        else:
            self.env["FSGS_STRETCH"] = "0"

        if self.border() == self.SMALL_BORDER:
            self.env["FSGS_BORDER"] = "1"
        elif self.border() == self.LARGE_BORDER:
            self.env["FSGS_BORDER"] = "2"
        else:
            self.env["FSGS_BORDER"] = "0"

        # env["FSGS_WINDOW_TITLE"] = ""
        self.set_environment_path(
            env, "FSGS_SCREENSHOTS_DIR", self.screenshots_dir())
        self.set_environment_path(
            env, "FSGS_SCREENSHOTS_BASE", self.screenshots_base())
        if self._model_name:
            env["FSGS_WINDOW_TITLE"] = self._model_name

        env.update(self.env)
        if not self.emulator.allow_home_access:
            env["HOME"] = self.home.path

        if not self._allow_gsync:
            # DOSBox-FS and Fuse-FS does not work nicely with G-SYNC yet.
            # Enabling G-SYNC causes stuttering.
            # Update: Should work fine with DOSBox-FS now...
            env["__GL_GSYNC_ALLOWED"] = "0"
            # Disable V-Sync
            env["__GL_SYNC_TO_VBLANK"] = "0"

        # Make sure we are allowed to flip buff ers faster than the screen
        # refresh rate, important for e.g. DOSBox @70Hz.
        # https://dri.freedesktop.org/wiki/ConfigurationOptions/
        # 1 = Application preference, default interval 0
        # Update: Not needed when emulators explicitly set swap interval 0.
        # env["vblank_mode"] = "1"

        self.update_environment_with_centering_info(env)

    def update_environment_with_centering_info(self, env):
        # FIXME: does not really belong here (dependency loop)
        from launcher.launcher_config import LauncherConfig
        from launcher.launcher_settings import LauncherSettings
        width = (LauncherConfig.get("window_width") or
                 LauncherSettings.get("window_width"))
        height = (LauncherConfig.get("window_height") or
                  LauncherSettings.get("window_height"))
        try:
            width = int(width)
        except:
            width = 960
        try:
            height = int(height)
        except:
            height = 540
        from launcher.ui.launcherwindow import LauncherWindow
        if LauncherWindow.current() is None:
            return

        main_w, main_h = LauncherWindow.current().get_size()
        main_x, main_y = LauncherWindow.current().get_position()

        x = main_x + (main_w - width) // 2
        y = main_y + (main_h - height) // 2

        # FIXME: REMOVE
        env["FSGS_WINDOW_X"] = str(x)
        env["FSGS_WINDOW_Y"] = str(y)

        # FIXME: REMOVE
        env["SDL_VIDEO_WINDOW_POS"] = str("{0},{1}".format(x, y))

        env["FSGS_WINDOW_CENTER"] = "{0},{1}".format(
            main_x + main_w // 2, main_y + main_h // 2)

        # args.append("--window-x={0}".format(x))
        # args.append("--window-y={0}".format(y))
        # print("window position", env["SDL_VIDEO_WINDOW_POS"])
        # os.environ["SDL_VIDEO_WINDOW_POS"] = "{0},{1}".format(x, y)

    def prepare_emulator_skin(self, env):
        path = self.temp_file("left.png").path
        with open(path, "wb") as f:
            f.write(Resources("fsgs").stream("res/emu/left.png").read())
        env["FSGS_SKIN_LEFT"] = path
        path = self.temp_file("right.png").path
        with open(path, "wb") as f:
            f.write(Resources("fsgs").stream("res/emu/right.png").read())
        env["FSGS_SKIN_RIGHT"] = path

    def start_emulator(
            self, emulator, args=None, env_vars=None, executable=None,
            cwd=None):
        # if "/" in emulator:
        #     if not executable:
        #         executable = self.find_emulator_executable(emulator)
        #     if not executable:
        #         emulator = emulator.split("/")[-1]
        #
        # if not executable:
        #     executable = self.find_emulator_executable("fs-" + emulator)
        # if not executable:
        #     executable = self.find_emulator_executable(emulator)
        #
        # if not executable:
        #     raise Exception("could not find executable for " + emulator)

        args = []
        args.extend(self.args)

        if "SDL_VIDEODRIVER" in os.environ:
            print("SDL_VIDEODRIVER was present in environment, removing!")
            del os.environ["SDL_VIDEODRIVER"]

        env = os.environ.copy()
        FSUAE.add_environment_from_settings(env)
        self.update_environment(env)
        self.prepare_emulator_skin(env)
        if env_vars:
            env.update(env_vars)
        print("")
        for key in sorted(env.keys()):
            print("[ENV]", key, ":", repr(env[key]))
        print("")
        for arg in args:
            print("[ARG]", repr(arg))
        print("")

        kwargs = {}
        if env is not None:
            kwargs["env"] = env
        if cwd is not None:
            kwargs["cwd"] = cwd
        else:
            kwargs["cwd"] = self.cwd.path
        print("[CWD]", kwargs["cwd"])
        print("")
        if System.windows:
            kwargs["close_fds"] = True
        # print(" ".join(args))
        current_task.set_progress(
            "Starting {emulator}".format(emulator=emulator))
        # import subprocess
        # return subprocess.Popen(["strace", emulator.path] + args, **kwargs)
        return emulator.popen(args, **kwargs)
        # return process

    def find_emulator_executable(self, name):
        # if os.path.isdir("../fs-uae/src"):
        #     # running from source directory, we then want to find locally
        #     # compiled binaries if available
        #     path = "../fs-uae/fs-uae"
        #     if System.windows:
        #         path += ".exe"
        #     if os.path.isfile(path):
        #         return path
        #     raise Exception("Could not find development FS-UAE executable")

        if "/" in name:
            package, name = name.split("/")
        else:
            package = name

        if System.windows:
            # first we check if the emulator is bundled inside the launcher
            # directory
            exe = os.path.join(
                fsboot.executable_dir(), package, name + ".exe")
            if not os.path.exists(exe):
                # for when the emulators are placed alongside the launcher /
                # game center directory
                exe = os.path.join(
                    fsboot.executable_dir(), "..", package, name + ".exe")
            if not os.path.exists(exe):
                # when the emulators are placed alongside the fs-uae/ directory
                # containing launcher/, for FS-UAE Launcher & FS-UAE Arcade
                exe = os.path.join(
                    fsboot.executable_dir(), "..", "..", package, name + ".exe")
            if not os.path.exists(exe):
                return None
            return exe
        elif System.macos:
            exe = os.path.join(
                fsboot.executable_dir(), "..",
                package + ".app", "Contents", "MacOS", name)
            if not os.path.exists(exe):
                exe = os.path.join(
                    fsboot.executable_dir(), "..", "..", "..",
                    package + ".app", "Contents", "MacOS", name)
            if not os.path.exists(exe):
                exe = os.path.join(
                    "/Applications",
                    package + ".app", "Contents", "MacOS", name)
            if not os.path.exists(exe):
                return None
            return exe

        if os.path.exists("/opt/{0}/bin/{1}".format(package, name)):
            return "/opt/{0}/bin/{1}".format(package, name)

        if package == name:
            for directory in os.environ["PATH"].split(":"):
                path = os.path.join(directory, name)
                if os.path.exists(path):
                    return path
        return None

    def get_game_refresh_rate(self):
        """Override in inherited classes to specify custom refresh rate."""
        if self.options[Option.REFRESH_RATE]:
            print("get_game_refresh_rate, refresh_rate was set")
            return float(self.options[Option.REFRESH_RATE])
        if self.options[Option.VIDEO_STANDARD] == "NTSC":
            return 59.94
        if self.options[Option.VIDEO_STANDARD] == "PAL":
            return 50
        variant_name = self.variant_name()
        print("get_game_refresh_rate, variant name =", variant_name)
        if "USA" in variant_name:
            return 59.94
        if "World" in variant_name:
            return 59.94
        if "Japan" in variant_name:
            return 59.94
        if "Europe" in variant_name:
            return 50
        print("get_game_refresh_rate: unknown")
        return 0

    def configure_vsync(self):
        print("\n" + "-" * 79 + "\n" + "CONFIGURE VSYNC")
        # print("^" * 80)
        allow_vsync = self.use_vsync()
        # if self.get_option('vsync'):
        if allow_vsync:
            # try:
            #     game_refresh = float(self.options["refresh_rate"])
            # except Exception:
            game_refresh = self.get_game_refresh_rate() or 0.0
            # if self.context.game.config.get('system', '') == 'NTSC':
            #     game_refresh = 60.0
            # else:
            #     game_refresh = 50.0

            # refresh_rate_tool = RefreshRateTool(
            #     game_platform=self.fsgc.game.platform.id,
            #     game_refresh=round(game_refresh))
            # refresh_rate_tool.set_best_mode()
            # if refresh_rate_tool.allow_vsync():
            #     print("setting vsync to true")
            #     self.set_vsync(True)
            #     return refresh_rate_tool.get_display_refresh()
            screen_refresh = self.screen_refresh_rate()
            if self.options[Option.ASSUME_REFRESH_RATE]:
                try:
                    screen_refresh = float(
                        self.options[Option.ASSUME_REFRESH_RATE])
                except ValueError:
                    print("Could not parse 'assume_refresh_rate' value")
                else:
                    print("Assuming screen refresh rate:", screen_refresh)

            print("Game refresh rate:", game_refresh)
            print("Screen refresh rate:", screen_refresh)
            if int(round(screen_refresh)) == int(round(game_refresh)):
                print("setting vsync to true")
                self.set_vsync(True)
                return True
        else:
            print("vsync is not enabled")
        print("setting vsync to false")
        self.set_vsync(False)
        return False

    def set_vsync(self, vsync):
        print("GameRunner - set vsync to", vsync)
        self.__vsync = vsync

    def abort(self):
        print("GameRunner.abort - WARNING: not implemented")


class Port(object):
    def __init__(self, name):
        self.name = name
        self.types = []
        self.index = 0
        self.device = None

        # FIXME: remove
        self.device_id = None
        self.device_config = None

    @property
    def type(self):
        return self.types[self.index]["type"]

    @property
    def mapping_name(self):
        return self.types[self.index]["mapping_name"]

    @property
    def description(self):
        return self.types[self.index]["description"]


class TemporaryItem:
    def __init__(self, root, prefix="tmp", suffix="", directory=False):
        self.root = root
        self.prefix = prefix
        self.suffix = suffix
        self._path = None
        self.directory = directory

    def __del__(self):
        self.delete()

    def delete(self):
        print("[DRIVER] TemporaryItem.delete")
        assert self.root is None
        if self._path is None:
            return
        if os.environ.get("FSGS_CLEANUP", "") == "0":
            print("[DRIVER] NOTICE: keeping temp files around...")
            return
        if self._path:
            print("[DRIVER] Removing", self._path)
            shutil.rmtree(self._path)
            self._path = None

    @property
    def path(self):
        if self._path is None:
            if hasattr(self.root, "path"):
                # We want to delay temp dir creation as long as possible,
                # so we only call root.path when we have to.
                root = self.root.path
            else:
                root = self.root
            if self.directory:
                self._path = tempfile.mkdtemp(
                    prefix=self.prefix, suffix=self.suffix, dir=root)
            else:
                fd, self._path = tempfile.mkstemp(
                    prefix=self.prefix, suffix=self.suffix, dir=root)
                os.close(fd)
        return self._path


class TemporaryNamedItem:
    def __init__(self, root, name, directory=False):
        self.root = root
        self.name = name
        self._path = None
        self.directory = directory

    @property
    def path(self):
        if self._path is None:
            root = self.root.path
            self._path = os.path.join(root, self.name)
            if not os.path.exists(self._path):
                if self.directory:
                    os.makedirs(self._path)
                else:
                    with open(self.path, "wb"):
                        pass
        return self._path


class GameEmulator:
    def __init__(self):
        self.name = "no-emulator"
        self.args = []
        self.env = {}
        self.process = None
        # self.allow_system_emulator = False
        self.allow_home_access = False


class GameFiles:
    def __init__(self, fsgc):
        self.fsgc = fsgc
        self._files = []

    def add(self, dest, source=None, sha1=None, description=None):
        self._files.append({
            "source": source,
            "sha1": sha1,
            "dest": dest,
            "description": description,
        })

    def install(self):
        for file in self._files:
            # uri = self.fsgc.file.find_by_sha1(tos_file.sha1)
            # if not uri:
            #     raise Exception(
            #             "Could not find {} (SHA-1: {})".format(
            #                 tos_file.name, tos_file.sha1))
            # self.files.add(self.tos_file.path, source=uri)
            if file["source"]:
                self.fsgc.file.copy_game_file(file["source"], file["dest"])
            else:
                assert file["sha1"]
                uri = self.fsgc.file.find_by_sha1(file["sha1"])
                if not uri:
                    description = file["description"] or \
                                  os.path.basename(file["dest"])
                    raise Exception(
                        "Could not find {} (SHA-1: {})".format(
                            description, file["sha1"]))
                self.fsgc.file.copy_game_file(uri, file["dest"])
