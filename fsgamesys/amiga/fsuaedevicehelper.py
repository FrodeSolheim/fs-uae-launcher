import os
import subprocess
from typing import Dict, List, Optional

from fsbc.settings import Settings
from fsgamesys.amiga.fsuae import FSUAE
from fsgamesys.options.option import Option
from fsgamesys.plugins.pluginexecutablefinder import PluginExecutableFinder


class FSUAEDeviceHelper:
    @classmethod
    def start_with_args(cls, args: List[str], stdout: Optional[int] = None):
        print("FSUAEDeviceHelper.start_with_args:", args)
        exe = PluginExecutableFinder().find_executable("fs-uae-device-helper")
        if not exe:
            raise RuntimeError(
                "Could not find fs-uae-device-helper executable"
            )
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
            stdout=stdout,
            stdin=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        return process

    @classmethod
    def maybe_add_fake_joysticks(cls, env: Dict[str, str]):
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
