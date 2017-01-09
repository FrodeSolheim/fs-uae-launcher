import sys

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
