import os
import subprocess

from fsbc.settings import Settings
from fsgs.amiga.fsuae import FSUAE
from fsgs.options.option import Option


class FSUAEDeviceHelper:
    @classmethod
    def start_with_args(cls, args, **kwargs):
        print("FSUAEDeviceHelper.start_with_args:", args)
        exe = cls.find_executable()
        print("Current dir (cwd): ", os.getcwd())
        print("Using executable:", exe)
        args = [exe] + args
        print(args)
        env = os.environ.copy()
        cls.maybe_add_fake_joysticks(env)
        FSUAE.add_environment_from_settings(env)
        process = subprocess.Popen(
            args,
            env=env,
            stdin=subprocess.PIPE,
            stderr=subprocess.PIPE,
            **kwargs
        )
        return process

    @classmethod
    def find_executable(cls):
        return FSUAE.find_executable("fs-uae-device-helper", libexec=True)

    @classmethod
    def maybe_add_fake_joysticks(cls, env):
        settings = Settings.instance()
        if settings.get(Option.FAKE_JOYSTICKS):
            try:
                fake_joysticks = int(settings.get(Option.FAKE_JOYSTICKS))
            except ValueError:
                print(
                    "WARNING: fake_joysticks contains invalid value",
                    repr(settings.get(Option.FAKE_JOYSTICKS)),
                )
            else:
                env["FSGS_FAKE_JOYSTICKS"] = str(fake_joysticks)
