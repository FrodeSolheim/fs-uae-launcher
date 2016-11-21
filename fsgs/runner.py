import os
import shutil
import io
import tempfile
import warnings
from collections import defaultdict

from fsgs.amiga.FSUAE import FSUAE

import fsboot
from fsbc.application import Application
from fsbc.system import windows, macosx
from fsbc.task import current_task
from fsgs.plugins.plugin_manager import PluginManager
from fsgs.refreshratetool import RefreshRateTool
from fsgs.FSGSDirectories import FSGSDirectories
from fsgs.util.gamenameutil import GameNameUtil
from fsbc.settings import Settings


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
        print("TemporaryItem.delete")
        assert self.root is None
        if self._path is None:
            return
        if os.environ.get("FSGS_CLEANUP", "") == "0":
            print("NOTICE: keeping temp files around...")
            return
        if self._path:
            print("Removing", self._path)
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


# noinspection PyMethodMayBeStatic
class GameRunner(object):

    PORTS = []

    def __init__(self, fsgs):
        self.fsgs = fsgs
        self.args = []
        self.env = {}
        self.emulator = "no-emulator"

        self.config = defaultdict(str)
        for key, value in Settings.instance().values.items():
            # FIXME: re-enable this check?
            # if key in Config.config_keys:
            #     print("... ignoring config key from settings:", key)
            #     continue
            self.config[key] = value

        for key, value in self.fsgs.config.items():
            self.config[key] = value

        self.ports = []
        for port_info in self.PORTS:
            port = Port(port_info["description"])
            port.types = port_info["types"]
            self.ports.append(port)

        self.__vsync = False
        self.__game_temp_file = None
        self.temp_root = TemporaryItem(
            root=None, prefix="fsgs-", suffix="tmp", directory=True)

        # self.cwd = self.create_temp_dir("cwd")
        # self.home = self.cwd

        # Default current working directory for the emulator.
        self.cwd = self.temp_dir("cwd")
        # Fake home directory for the emulator.
        self.home = self.temp_dir("home")

    def __del__(self):
        print("GameRunner.__del__")

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
        return self.config.get("video_sync") in ["1", "auto"]

    def use_doubling(self):
        return True

    def use_smoothing(self):
        return True

    def use_stretching(self):
        # if "--no-stretch" in sys.argv:
        #     return False
        if Settings.instance()["keep_aspect"] == "1":
            return
        # if Settings.instance()["stretch"] == "0":
        #     return False
        return True

    def use_audio_frequency(self):
        if Settings.instance()["audio_frequency"]:
            try:
                return int(Settings.instance()["audio_frequency"])
            except ValueError:
                pass
        return 48000

    def screenshots_dir(self):
        return FSGSDirectories.screenshots_output_dir()

    def screenshots_name(self):
        return GameNameUtil.create_fs_name(self.get_name())

    # def get_game_name(self):
    #     return self.config["game_name"]
    #
    # def get_variant_name(self):
    #     return self.config["variant_name"]

    def get_platform_name(self):
        p = self.config["platform"].lower()
        print(p)
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

            if windows or macosx:
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
        monitor = self.config.get("monitor", "")
        return self.screen_refresh_rate_for_monitor(monitor)

    @classmethod
    def screen_index_for_monitor(cls, monitor):
        rect = cls.screen_rect_for_monitor(monitor)
        for i, s in enumerate(cls._screens()):
            if rect == (s[2].x(), s[2].y(), s[2].width(), s[2].height()):
                return i
        raise Exception("Could not find screen at position {}".format(rect))

    def screen_index(self):
        monitor = self.config.get("monitor", "")
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
        monitor = self.config.get("monitor", "")
        return self.screen_rect_for_monitor(monitor)

    def get_name(self):
        # return "{0} ({1}, {2})".format(
        #     self.get_game_name(), self.get_platform_name(),
        #     self.get_variant_name())
        return "{0} ({1}, {2})".format(
            self.fsgs.game.name, self.fsgs.game.platform.name,
            self.fsgs.game.variant.name)

    def get_state_dir(self):
        state_dir = os.path.join(
            FSGSDirectories.get_save_states_dir(),
            GameNameUtil.create_fs_name(self.get_name()))
        if not os.path.exists(state_dir):
            os.makedirs(state_dir)
        if self.fsgs.game.variant.uuid:
            uuid_file = os.path.join(state_dir, "uuid.txt")
            with io.open(uuid_file, "w", encoding="UTF-8") as f:
                f.write(self.fsgs.game.variant.uuid + "\n")
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

    def get_game_file(self, config_key="cartridge"):
        if self.__game_temp_file is not None:
            return self.__game_temp_file.path

        file_uri = self.config[config_key]
        # FIXME: create new API fsgs.file.path(file_uri), returns path
        # (and creates temp file if necessary)
        input_stream = self.fsgs.file.open(file_uri)

        # self.__game_temp_file = self.fsgs.temp_file(file_uri.split("/")[-1])
        self.__game_temp_file = TemporaryNamedItem(
            self.temp_root, file_uri.split("/")[-1])

        with open(self.__game_temp_file.path, "wb") as f:
            f.write(input_stream.read())
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

    def run(self):
        executable = PluginManager.instance().find_executable(self.emulator)
        if executable is None:
            raise LookupError("Could not find emulator " + repr(self.emulator))
        return self.start_emulator(executable)

    def start_emulator_from_plugin_resource(
            self, provide_name, args=None, env_vars=None):
        resource = self.fsgs.plugins.find_executable(provide_name)
        if resource is None:
            raise Exception("Could not find emulator " + repr(provide_name))
        if env_vars is None:
            env_vars = os.environ.copy()
        # Set LD_LIBRARY_PATH for Linux plugins with bundled libraries
        env_vars["LD_LIBRARY_PATH"] = os.path.dirname(resource.path)
        return self.start_emulator("", args=args, env_vars=env_vars,
                                   executable=resource.path)

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
        print(repr(args))

        if "SDL_VIDEODRIVER" in os.environ:
            print("SDL_VIDEODRIVER was present in environment, removing!")
            del os.environ["SDL_VIDEODRIVER"]

        env = os.environ.copy()
        FSUAE.add_environment_from_settings(env)
        if self.use_fullscreen():
            fullscreen_mode = self.config.get("fullscreen_mode", "")

            x, y, w, h = self.screen_rect()
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

        env.update(self.env)
        env["HOME"] = self.home.path

        if env_vars:
            env.update(env_vars)
        print(env)

        kwargs = {}
        if env is not None:
            kwargs["env"] = env
        if cwd is not None:
            kwargs["cwd"] = cwd
        else:
            kwargs["cwd"] = self.cwd.path
        if windows:
            kwargs["close_fds"] = True
        print(" ".join(args))
        current_task.set_progress(
            "Starting {emulator}".format(emulator=emulator))
        # process = subprocess.Popen(*args, **kwargs)
        return emulator.popen(args, **kwargs)
        # return process

    def find_emulator_executable(self, name):
        # if os.path.isdir("../fs-uae/src"):
        #     # running from source directory, we then want to find locally
        #     # compiled binaries if available
        #     path = "../fs-uae/fs-uae"
        #     if windows:
        #         path += ".exe"
        #     if os.path.isfile(path):
        #         return path
        #     raise Exception("Could not find development FS-UAE executable")

        if "/" in name:
            package, name = name.split("/")
        else:
            package = name

        if windows:
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
        elif macosx:
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
        if self.config["refresh_rate"]:
            return float(self.config["refresh_rate"])
        if self.config.get("video_standard") == "NTSC":
            return 59.94
        if self.config.get("video_standard") == "PAL":
            return 50
        if "USA" in self.fsgs.game.variant.name:
            return 59.94
        if "World" in self.fsgs.game.variant.name:
            return 59.94
        if "Japan" in self.fsgs.game.variant.name:
            return 59.94
        if "Europe" in self.fsgs.game.variant.name:
            return 50

    def configure_vsync(self):
        print("\n" + "-" * 79 + "\n" + "CONFIGURE VSYNC")
        # print("^" * 80)
        allow_vsync = self.use_vsync()
        # if self.get_option('vsync'):
        if allow_vsync:
            # try:
            #     game_refresh = float(self.config["refresh_rate"])
            # except Exception:
            game_refresh = self.get_game_refresh_rate() or 0.0
            # if self.context.game.config.get('system', '') == 'NTSC':
            #     game_refresh = 60.0
            # else:
            #     game_refresh = 50.0

            # refresh_rate_tool = RefreshRateTool(
            #     game_platform=self.fsgs.game.platform.id,
            #     game_refresh=round(game_refresh))
            # refresh_rate_tool.set_best_mode()
            # if refresh_rate_tool.allow_vsync():
            #     print("setting vsync to true")
            #     self.set_vsync(True)
            #     return refresh_rate_tool.get_display_refresh()
            screen_refresh = self.screen_refresh_rate()
            if self.config["assume_refresh_rate"]:
                try:
                    screen_refresh = float(self.config["assume_refresh_rate"])
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

    def finish(self):
        pass
