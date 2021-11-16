import os
import subprocess
import tempfile
from typing import Dict, List, Optional

from fsbc.application import Application
from fsgamesys.plugins.pluginexecutablefinder import PluginExecutableFinder


class FSUAE(object):
    @classmethod
    def start_with_config(cls, config: str, cwd: Optional[str] = None):
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
    def start_with_args(
        cls,
        args: List[str],
        cwd: Optional[str] = None,
        stdout: Optional[int] = None,
    ):
        print("FSUAE.start_with_args:", args)
        exe = PluginExecutableFinder().find_executable("fs-uae")
        if not exe:
            raise RuntimeError("Could not find fs-uae executable")
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

        cls.add_environment_from_settings(env)
        # env["SDL_VIDEO_WINDOW_POS"] = "0,0"
        # args += ["--fullscreen-mode", "desktop"]

        # No longer needed since Python 3.4?
        # if windows:
        #     p = subprocess.Popen(
        #         args, cwd=cwd, env=env, close_fds=True, **kwargs
        #     )
        # else:

        p = subprocess.Popen(args, cwd=cwd, env=env, stdout=stdout)
        return p

    @classmethod
    def add_environment_from_settings(cls, env: Dict[str, str]):
        try:
            values = Application.getInstance().settings.values
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
