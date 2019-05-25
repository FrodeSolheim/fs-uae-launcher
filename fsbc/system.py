import sys
import platform as _platform

windows = sys.platform == "win32"
linux = sys.platform.startswith("linux")
macosx = sys.platform == "darwin"

if windows:
    platform = "windows"
elif linux:
    platform = "linux"
elif macosx:
    platform = "macos"
else:
    platform = "unknown"


class System:
    windows = windows
    linux = linux
    macos = macosx
    platform = platform

    x86_64 = False
    if _platform.machine().lower() in [
        "x86_64",
        "x86-64",
        "amd64",
        "i386",
        "i486",
        "i586",
        "i686",
    ]:
        if _platform.architecture()[0] == "64bit":
            x86_64 = True
        # else:
        #     x86 = True
