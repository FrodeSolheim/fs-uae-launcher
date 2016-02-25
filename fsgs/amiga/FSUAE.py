import os
import tempfile
import traceback
import subprocess
from fsbc.system import windows, macosx
from fsbc.application import Application, app

try:
    getcwd = os.getcwdu
except AttributeError:
    getcwd = os.getcwd


class FSUAE(object):

    @classmethod
    def start_with_config(cls, config):
        print("FSUAE.start_with_config:")
        tf = tempfile.NamedTemporaryFile(suffix=".fs-uae", delete=False)
        config_file = tf.name
        with tf:
            for line in config:
                print(line)
                tf.write(line.encode("UTF-8"))
                tf.write(b"\n")
        args = [config_file]
        return cls.start_with_args(args), config_file

    @classmethod
    def start_with_args(cls, args, **kwargs):
        print("FSUAE.start_with_args:", args)
        exe = cls.find_executable()
        print("current dir (cwd): ", getcwd())
        print("using fs-uae executable:", exe)
        args = [exe] + args

        # if "--always-on-top" in sys.argv:
        #     args += ["--always-on-top"]

        print(args)
        for name in ["SDL_VIDEODRIVER", "__GL_SYNC_TO_VBLANK"]:
            if name in os.environ:
                print("{0} was present in environment, removing!".format(name))
                del os.environ[name]
        env = os.environ.copy()
        print(repr(env))
        # env = None
        try:
            cls.center_window(args, env)
        except Exception:
            traceback.print_exc()
        cls.add_environment_from_settings(env)
        # env[str("SDL_VIDEO_WINDOW_POS")] = "0,0"
        # args += ["--fullscreen-mode", "desktop"]
        if windows:
            p = subprocess.Popen(args, env=env, close_fds=True, **kwargs)
        else:
            p = subprocess.Popen(args, env=env, **kwargs)
        return p

    @classmethod
    def add_environment_from_settings(cls, env):
        try:
            values = app.settings.values
        except AttributeError:
            values = {}

        for key, value in values.items():
            # if not key.startswith("environment_"):
            #     continue
            # key = key[12:].upper()
            if not key.isupper():
                continue
            # Check if it looks like a valid environment variable
            for c in key:
                if c not in "ABCDEFGHIJKLMNOPQRSTUVWXYZ_0123456789":
                    break
            else:
                print("[ENV] {} = {}".format(key, value))
                env[key] = value

    @classmethod
    def center_window(cls, args, env):
        # FIXME: does not really belong here (dependency loop)
        from launcher.launcher_config import LauncherConfig
        from launcher.launcher_settings import LauncherSettings
        width = LauncherConfig.get("window_width") or LauncherSettings.get("window_width")
        height = LauncherConfig.get("window_height") or LauncherSettings.get("window_height")
        try:
            width = int(width)
        except:
            width = 960
        try:
            height = int(height)
        except:
            height = 540
        from launcher.ui.launcher_window import LauncherWindow
        if LauncherWindow.current() is None:
            return

        main_w, main_h = LauncherWindow.current().get_size()
        main_x, main_y = LauncherWindow.current().get_position()

        x = main_x + (main_w - width) // 2
        y = main_y + (main_h - height) // 2

        # FIXME: reimplement without wx
        # if windows:
        #     import wx
        #    y += wx.SystemSettings_GetMetric(wx.SYS_CAPTION_Y)

        env[str("SDL_VIDEO_WINDOW_POS")] = str("{0},{1}".format(x, y))
        args.append("--window-x={0}".format(x))
        args.append("--window-y={0}".format(y))
        # print("window position", env["SDL_VIDEO_WINDOW_POS"])
        # os.environ["SDL_VIDEO_WINDOW_POS"] = "{0},{1}".format(x, y)

    @classmethod
    def find_executable(cls, executable="fs-uae"):
        application = Application.instance()

        if os.path.isdir("../fs-uae/src"):
            # running FS-UAE Launcher from source directory, we
            # then want to run the locally compiled fs-uae binary
            path = "../fs-uae/" + executable
            if windows:
                path += ".exe"
            if os.path.isfile(path):
                return path
            raise Exception("Could not find development FS-UAE executable")

        if windows:
            exe = os.path.join(
                application.executable_dir(), executable + ".exe")
            if not os.path.exists(exe):
                exe = os.path.join(
                    application.executable_dir(),
                    "fs-uae/" + executable + ".exe")
            if not os.path.exists(exe):
                exe = os.path.join(
                    application.executable_dir(), "../" + executable + ".exe")
        elif macosx:
            exe = os.path.join(application.executable_dir(), executable)
            if not os.path.exists(exe):
                exe = os.path.join(
                    application.executable_dir(),
                    "../FS-UAE.app/Contents/MacOS/" + executable)
            if not os.path.exists(exe):
                exe = os.path.join(
                    application.executable_dir(),
                    "../../../FS-UAE.app/Contents/MacOS/" + executable)
            if not os.path.exists(exe):
                exe = os.path.join(
                    application.executable_dir(),
                    "../../../Programs/Mac OS X/FS-UAE.app/Contents/MacOS/" + executable)
            if not os.path.exists(exe):
                exe = os.path.join(
                    application.executable_dir(),
                    "../../../FS-UAE Launcher.app/Contents/Resources/"
                    "FS-UAE.app/Contents/MacOS/" + executable)
        else:
            print("application executable dir", application.executable_dir())
            exe = os.path.join(application.executable_dir(), executable)
            print("checking", exe)
            if not os.path.exists(exe):
                exe = os.path.join(
                    application.executable_dir(), "..", "bin", executable)
                print("checking", exe)
            if not os.path.exists(exe):
                return executable

        if not os.path.exists(exe):
            raise Exception("Could not find {0} executable".format(
                repr(executable)))
        return exe
