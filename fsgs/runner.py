import os
import sys
import io
import subprocess
from collections import defaultdict
from fsbc.Application import app
from fsbc.system import windows, macosx
from fsbc.task import current_task
from fsgs.refreshratetool import RefreshRateTool
from fsgs.FSGSDirectories import FSGSDirectories
from fsgs.util.gamenameutil import GameNameUtil


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


class GameRunner(object):

    PORTS = []

    def __init__(self, fsgs):
        self.fsgs = fsgs
        self.__env = {}
        self.__args = []

        self.config = defaultdict(str)
        for key, value in app.settings.values.items():
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

        # default current working directory for emulator
        self.cwd = self.create_temp_dir("cwd")
        self.home = self.cwd

    # self.inputs.append(self.create_input(
    #         name='Controller {0}'.format(i + 1),
    #         type='megadrive',
    #         description='Gamepad'))

    def use_fullscreen(self):
        # FIXME: not a very nice hack to hard-code application name here...
        if app.name == "fs-uae-arcade":
            return True
        if app.settings["fullscreen"] == "0":
            return False
        return True

    def use_vsync(self):
        # if "--no-vsync" in sys.argv:
        #     return False
        # return True
        return self.config.get("video_sync") == "1"

    def use_doubling(self):
        return True

    def use_smoothing(self):
        return True

    def use_stretching(self):
        if "--no-stretch" in sys.argv:
            return False
        if app.settings["stretch"] == "0":
            return False
        return True

    def use_audio_frequency(self):
        if app.settings["audio_frequency"]:
            try:
                return int(app.settings["audio_frequency"])
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
        refresh_rate_tool = RefreshRateTool()
        # FIXME: screen size monitor size
        width = refresh_rate_tool.get_current_mode()["width"]
        height = refresh_rate_tool.get_current_mode()["height"]
        # if width > 2 * height:
        #     print("width > 2 * height, assuming dual-monitor setup...")
        #     return width // 2, height
        return width, height

    def screen_rect(self):
        try:
            desktop = app.qapplication.desktop()
        except AttributeError:
            # no QApplication, probably not running via QT
            # FIXME: log warning
            return 0, 0, 640, 480
        screens = []
        for i in range(desktop.screenCount()):
            geometry = desktop.screenGeometry(i)
            screens.append([geometry.x(), i, geometry])
        screens.sort()
        monitor = self.config.get("monitor", "")
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

    def get_screen_width(self):
        """deprecated"""
        return self.screen_size()[0]

    def get_screen_height(self):
        """deprecated"""
        return self.screen_size()[1]

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

        self.__game_temp_file = self.fsgs.temp_file(file_uri.split("/")[-1])

        with open(self.__game_temp_file.path, "wb") as f:
            f.write(input_stream.read())
        return self.__game_temp_file.path

    def create_temp_dir(self, suffix):
        return self.fsgs.temp_dir(suffix)

    def create_temp_file(self, suffix):
        return self.fsgs.temp_file(suffix)

    def set_env(self, name, value):
        self.__env[name] = value

    def add_arg(self, *args):
        self.__args.extend(args)

    def start_emulator_from_plugin_resource(
            self, provide_name, args=None, env_vars=None):
        resource = self.fsgs.plugins.find_executable(provide_name)
        return self.start_emulator("", args=args, env_vars=env_vars,
                                   executable=resource.path)

    def start_emulator(
            self, emulator, args=None, env_vars=None, executable=None,
            cwd=None):
        if "/" in emulator:
            if not executable:
                executable = self.find_emulator_executable(emulator)
            if not executable:
                emulator = emulator.split("/")[-1]

        if not executable:
            executable = self.find_emulator_executable("fs-" + emulator)
        if not executable:
            executable = self.find_emulator_executable(emulator)

        if not executable:
            raise Exception("could not find executable for " + emulator)
        process_args = [executable]
        process_args.extend(self.__args)
        if args is not None:
            process_args.extend(args)
        print(repr(process_args))

        if "SDL_VIDEODRIVER" in os.environ:
            print("SDL_VIDEODRIVER was present in environment, removing!")
            del os.environ["SDL_VIDEODRIVER"]

        env = os.environ.copy()
        if self.use_fullscreen():
            for key in ["FSGS_GEOMETRY", "FSGS_WINDOW"]:
                if env.get(key, ""):
                    # Already specified externally, so we just use
                    # the existing values...
                    pass
                    print("using existing fullscreen window rect")
                else:
                    x, y, w, h = self.screen_rect()
                    env[key] = "{0},{1},{2},{3}".format(x, y, w, h)
            print("fullscreen rect:", env.get("FSGS_GEOMETRY", ""))

            if self.config.get("fullscreen_mode", "") == "window":
                print("using fullscreen window mode")
                env["FSGS_FULLSCREEN"] = "window"
            elif self.config.get("fullscreen_mode", "") == "fullscreen":
                print("using fullscreen (legacy) mode")
                env["FSGS_FULLSCREEN"] = "fullscreen"
            else:
                print("using fullscreen desktop mode")
                env["FSGS_FULLSCREEN"] = "desktop"
        else:
            print("using window mode (no fullscreen)")
            env["FSGS_FULLSCREEN"] = ""

        env.update(self.__env)
        env["HOME"] = self.home.path

        if env_vars:
            env.update(env_vars)
        print(env)

        args = [process_args]
        kwargs = {}
        if env is not None:
            kwargs["env"] = env
        if cwd is not None:
            kwargs["cwd"] = cwd
        else:
            kwargs["cwd"] = self.cwd.path
        if windows:
            kwargs["close_fds"] = True
        print(" ".join(process_args))
        current_task.set_progress(
            "Starting {emulator}".format(emulator=emulator))
        process = subprocess.Popen(*args, **kwargs)
        return process

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
                app.executable_dir(), package, name + ".exe")
            if not os.path.exists(exe):
                # for when the emulators are placed alongside the launcher /
                # game center directory
                exe = os.path.join(
                    app.executable_dir(), "..", package, name + ".exe")
            if not os.path.exists(exe):
                # when the emulators are placed alongside the fs-uae/ directory
                # containing launcher/, for FS-UAE Launcher & FS-UAE Arcade
                exe = os.path.join(
                    app.executable_dir(), "..", "..", package, name + ".exe")
            if not os.path.exists(exe):
                return None
            return exe
        elif macosx:
            exe = os.path.join(
                app.executable_dir(), "..",
                package + ".app", "Contents", "MacOS", name)
            if not os.path.exists(exe):
                exe = os.path.join(
                    app.executable_dir(), "..", "..", "..",
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
            for dir in os.environ["PATH"].split(":"):
                # dir = unicode_path(dir)
                path = os.path.join(dir, name)
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
            refresh_rate_tool = RefreshRateTool(
                game_platform=self.fsgs.game.platform.id,
                game_refresh=round(game_refresh))
            refresh_rate_tool.set_best_mode()
            if refresh_rate_tool.allow_vsync():
                print("setting vsync to true")
                self.set_vsync(True)
                return refresh_rate_tool.get_display_refresh()
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
