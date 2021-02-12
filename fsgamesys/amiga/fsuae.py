import os
import subprocess
import tempfile
import traceback

from fsbc.application import Application, app
from fscore.system import System
from fsgamesys.plugins.pluginmanager import Plugin

try:
    getcwd = os.getcwdu
except AttributeError:
    getcwd = os.getcwd


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
        exe = cls.find_executable()
        print("current dir (cwd): ", getcwd())
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

        cls.add_environment_from_settings(env)
        # env[str("SDL_VIDEO_WINDOW_POS")] = "0,0"
        # args += ["--fullscreen-mode", "desktop"]

        # No longer needed since Python 3.4?
        # if windows:
        #     p = subprocess.Popen(
        #         args, cwd=cwd, env=env, close_fds=True, **kwargs
        #     )
        # else:

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
    def find_executable(cls, executable="fs-uae", libexec=False):
        application = Application.instance()

        if os.path.basename(os.getcwd()).endswith("-private"):
            # We are running FS-UAE Launcher from source directory. We then
            # want to run the locally compiled fs-uae binary.
            path = "../fs-uae-private/" + executable
            if System.windows:
                path += ".exe"
            if os.path.isfile(path):
                return os.path.abspath(path)
            raise Exception("Could not find development FS-UAE executable")

        if os.path.isdir("../fs-uae/src"):
            # We are running FS-UAE Launcher from source directory. We then
            # want to run the locally compiled fs-uae binary.
            path = "../fs-uae/" + executable
            if System.windows:
                path += ".exe"
            if os.path.isfile(path):
                return os.path.abspath(path)
            raise Exception("Could not find development FS-UAE executable")

        if System.windows:
            exe = os.path.join(
                application.executable_dir(), executable + ".exe"
            )
            if not os.path.exists(exe):
                exe = os.path.join(
                    application.executable_dir(), "fs-uae", executable + ".exe"
                )
            if not os.path.exists(exe):
                exe = os.path.join(
                    application.executable_dir(), "..", executable + ".exe"
                )
            if not os.path.exists(exe):
                exe = os.path.join(
                    application.executable_dir(),
                    "..",
                    "..",
                    "..",
                    "FS-UAE",
                    Plugin.os_name(True),
                    Plugin.arch_name(True),
                    executable + ".exe",
                )
        elif System.macos:
            exe = os.path.join(application.executable_dir(), executable)
            if not os.path.exists(exe):
                exe = os.path.join(
                    application.executable_dir(),
                    "../FS-UAE.app/Contents/MacOS/" + executable,
                )
            if not os.path.exists(exe):
                exe = os.path.join(
                    application.executable_dir(),
                    "../../../FS-UAE.app/Contents/MacOS/" + executable,
                )
            if not os.path.exists(exe):
                exe = os.path.join(
                    application.executable_dir(),
                    "../../../FS-UAE Launcher.app/Contents/Resources/"
                    "FS-UAE.app/Contents/MacOS/" + executable,
                )
            if not os.path.exists(exe):
                exe = os.path.join(
                    application.executable_dir(),
                    "..",
                    "..",
                    "..",
                    "..",
                    "..",
                    "..",
                    "FS-UAE",
                    Plugin.os_name(True),
                    Plugin.arch_name(True),
                    "FS-UAE.app/Contents/MacOS/" + executable,
                )
                print("checking", exe)
        else:
            print("application executable dir", application.executable_dir())
            exe = os.path.join(application.executable_dir(), executable)
            print("Checking side-by-side:", exe)
            if not os.path.exists(exe) and libexec:
                exe = os.path.join(
                    application.executable_dir(), "..", "libexec", executable
                )
                print("Checking in $prefix/libexec:", exe)
            # if not os.path.exists(exe):
            #     exe = os.path.join(
            #         application.executable_dir(), "..", "bin", executable
            #     )
            #     print("checking", exe)
            # Find in plugin structure
            if not os.path.exists(exe):
                exe = os.path.join(
                    application.executable_dir(),
                    "..",
                    "..",
                    "..",
                    "FS-UAE",
                    Plugin.os_name(True),
                    Plugin.arch_name(True),
                    executable,
                )
                print("Checking plugin executable:", exe)
            if not os.path.exists(exe):
                print("Found ", exe)
                return executable

        if not os.path.exists(exe):
            raise Exception(
                "Could not find {0} executable".format(repr(executable))
            )
        return exe
