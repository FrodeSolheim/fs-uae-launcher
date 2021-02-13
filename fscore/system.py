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


def is_x86_64():
    if platform.machine().lower() in [
        "x86_64",
        "x86-64",
        "amd64",
        "i386",
        "i486",
        "i586",
        "i686",
    ]:
        return is_64_bit()
    else:
        return False


class System:
    linux = is_linux()
    macos = is_macos()
    windows = is_windows()
    x86_64 = is_x86_64()

    if linux:
        platform = "linux"
    elif macos:
        platform = "macos"
    elif windows:
        platform = "windows"
    else:
        platform = "unknown"
