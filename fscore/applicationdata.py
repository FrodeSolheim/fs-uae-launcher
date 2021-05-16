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
            os.path.join(Application.executableDir(), "pyproject.toml")
        ):
            return cls.Mode.DEVELOPMENT
        return cls.Mode.INSTALLED

    @classmethod
    def dataDir(cls) -> str:
        dataDirParts = [Application.executableDir()]
        mode = cls.mode()
        if mode == cls.Mode.DEVELOPMENT:
            dataDirParts.extend(["data"])
        elif mode == cls.Mode.INSTALLED:
            dataDirParts.extend(["..", "share", Application.shareDirName()])
        elif mode == cls.Mode.FROZEN:
            if System.macos:
                dataDirParts.extend(["..", "Resources", "Data"])
        elif mode == cls.Mode.PLUGIN_DATA:
            if System.macos:
                dataDirParts.extend(["..", ".."])
            dataDirParts.extend(["..", "..", "Data"])
        else:
            raise Exception(f"Unknown Datafile.mode ({mode})")
        return os.path.normpath(os.path.join(*dataDirParts))

    @classmethod
    def path(cls, relativePath: str) -> str:
        return os.path.join(cls.dataDir(), relativePath)

    @classmethod
    def stream(cls, relativePath: str) -> IO[bytes]:
        return open(cls.path(relativePath), "rb")

    @classmethod
    def pathOrStream(cls, relativePath: str) -> Union[str, IO[bytes]]:
        return cls.path(relativePath)
