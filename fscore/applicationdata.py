import os
from enum import Enum
from typing import IO, Union

import fsboot
from fscore.application import Application
from fscore.memoize import memoize
from fscore.system import System


class ApplicationData:
    class Mode(Enum):
        DEVELOPMENT = 0
        INSTALLED = 1
        FROZEN = 2
        PLUGIN_DATA = 3

    @classmethod
    @memoize
    def mode(cls) -> Mode:
        if fsboot.is_frozen():
            return cls.Mode.FROZEN
        elif os.path.exists(
            os.path.join(Application.executable_dir(), "pyproject.toml")
        ):
            return cls.Mode.DEVELOPMENT
        return cls.Mode.INSTALLED

    @classmethod
    def data_dir(cls) -> str:
        data_dir_parts = [Application.executable_dir()]
        mode = cls.mode()
        if mode == cls.Mode.DEVELOPMENT:
            data_dir_parts.extend(["data"])
        elif mode == cls.Mode.INSTALLED:
            data_dir_parts.extend(
                ["..", "share", Application.share_dir_name()]
            )
        elif mode == cls.Mode.FROZEN:
            if System.macos:
                data_dir_parts.extend(["..", "Resources", "Data"])
        elif mode == cls.Mode.PLUGIN_DATA:
            if System.macos:
                data_dir_parts.extend(["..", ".."])
            data_dir_parts.extend(["..", "..", "Data"])
        else:
            raise Exception(f"Unknown Datafile.mode ({mode})")
        data_dir = os.path.normpath(os.path.join(*data_dir_parts))
        return data_dir

    @classmethod
    def path(cls, relative_path: str) -> str:
        path = os.path.join(cls.data_dir(), relative_path)
        print("[DATA]", path)
        return path

    @classmethod
    def stream(cls, relative_path: str) -> IO[bytes]:
        return open(cls.path(relative_path), "rb")

    @classmethod
    def path_or_stream(cls, relative_path: str) -> Union[str, IO[bytes]]:
        return cls.path(relative_path)
