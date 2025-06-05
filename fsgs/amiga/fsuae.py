import os
import subprocess
import tempfile
import traceback

from fsbc.application import Application, app
from fsbc.system import macosx, windows
from fsgs.plugins.pluginexecutablefinder import PluginExecutableFinder
from fsgs.plugins.pluginmanager import Plugin


class FSUAE(object):
    @classmethod
    def start_with_config(cls, config, cwd=None):
        print("FSUAE.start_with_config:")
        tf = tempfile.NamedTemporaryFile(suffix=".fs-uae", delete=False)
        config_file = tf.name
        with tf:
            for line in config:
                print(line)
                tf.write(line.encode("UTF-8"))
                tf.write(b"\n")
        args = [config_file]
        return cls.start_with_args(args, cwd=cwd), config_file

    @classmethod
    def start_with_args(cls, args, cwd=None, **kwargs):
        print("FSUAE.start_with_args:", args)
        exe = PluginExecutableFinder().find_executable("fs-uae")
        if exe is None:
            raise Exception("Could not find fs-uae executable")
        print("current dir (cwd): ", os.getcwd())
        if cwd is not None:
            print("cwd override:", cwd)
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
            p = subprocess.Popen(
                args, cwd=cwd, env=env, close_fds=True, **kwargs
            )
        else:
            p = subprocess.Popen(args, cwd=cwd, env=env, **kwargs)
        return p

    @classmethod
    def add_environment_from_settings(cls, env):
        try:
            values = app.settings.values
        except AttributeError:
            values = {}
        for key, value in values.items():
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

        width = LauncherConfig.get("window_width") or LauncherSettings.get(
            "window_width"
        )
        height = LauncherConfig.get("window_height") or LauncherSettings.get(
            "window_height"
        )
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

        # FIXME: re-implement without wx
        # if windows:
        #     import wx
        #    y += wx.SystemSettings_GetMetric(wx.SYS_CAPTION_Y)

        env[str("SDL_VIDEO_WINDOW_POS")] = str("{0},{1}".format(x, y))
        args.append("--window-x={0}".format(x))
        args.append("--window-y={0}".format(y))
        # print("window position", env["SDL_VIDEO_WINDOW_POS"])
        # os.environ["SDL_VIDEO_WINDOW_POS"] = "{0},{1}".format(x, y)
