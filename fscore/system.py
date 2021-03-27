import platform
import sys


def is_linux():
    return sys.platform.startswith("linux")


def is_macos():
    return sys.platform == "darwin"


def is_windows():
    return sys.platform == "win32"


def is_64_bit():
    return platform.architecture()[0] == "64bit"


def is_x86_family():
    return platform.machine().lower() in [
        "x86_64",
        "x86-64",
        "amd64",
        "i386",
        "i486",
        "i586",
        "i686",
    ]


def is_x86_64():
    return is_64_bit() and is_x86_family()


class System:
    linux = is_linux()
    macos = is_macos()
    windows = is_windows()
    x86_64 = is_x86_64()

    if linux:
        platform = "linux"
        _operatingSystem = "Linux"
    elif macos:
        platform = "macos"
        _operatingSystem = "macOS"
    elif windows:
        platform = "windows"
        _operatingSystem = "Windows"
    else:
        platform = "unknown"
        _operatingSystem = "Unknown"

    @classmethod
    def getOperatingSystem(cls):
        return cls._operatingSystem

    @classmethod
    def getCpuArchitecture(cls):
        if is_x86_family():
            return "x86-64" if is_64_bit() else "x86"
        return "Unknown"
