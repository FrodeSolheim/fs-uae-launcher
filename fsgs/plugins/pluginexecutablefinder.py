from os import path
import platform
from typing import Union

from fsbc.system import System
import fsboot

X86_MACHINES = ["x86", "i386", "i486", "i586", "i686"]
X86_64_MACHINES = ["x86_64", "x86-64", "amd64"]
X86_ANY_MACHINES = X86_MACHINES + X86_64_MACHINES

# Mapping between executable name and plugin
known_executables = {
    "dosbox": "DOSBox",
    "dosbox-staging": "DOSBox-Staging",
    "fs-fuse": "FS-Fuse",
    "fs-uae": "FS-UAE",
    "fs-uae-device-helper": "FS-UAE",
    "fuse": "Fuse",
    "hatari": "Hatari",
    "mame": "MAME",
    "mednafen": "Mednafen",
    "x64sc": "Vice",
}


class PluginExecutableFinder:
    def find_executable(self, name: str):
        exe_file = find_executable(name)
        if exe_file:
            exe_file = path.normpath(exe_file)
            print("Normalized path:", exe_file)
            return exe_file
        return None


def find_executable(name: str):
    print("Find executable:", name)
    if fsboot.development():
        exe_file = find_development_executable(name)
        if exe_file:
            return exe_file
    exe_file = find_plugin_executable(name)
    if exe_file:
        return exe_file
    if fsboot.is_frozen():
        if System.macos:
            exe_file = find_side_by_side_app_executable(name)
            if exe_file:
                return exe_file
        exe_file = find_side_by_side_plugin_executable(name)
        if exe_file:
            return exe_file
    else:
        exe_file = find_side_by_side_executable(name)
        if exe_file:
            return exe_file
    return None


def get_current_plugin_dir() -> Union[str, None]:
    # Escape OS/Arch directories
    plugin_dir = path.join(fsboot.executable_dir(), "..", "..")
    if fsboot.is_frozen() and fsboot.is_macos():
        # Escape Contents/MacOS directories
        plugin_dir = path.join(plugin_dir, "..", "..")
    plugin_dir = path.normpath(plugin_dir)
    plugin_ini = path.join(plugin_dir, "Plugin.ini")
    if path.exists(plugin_ini):
        return plugin_dir
    return None
    # return plugin_dir


def find_development_executable(name: str):
    plugin_name = known_executables.get(name)
    if plugin_name is None:
        return None
    dir_name = plugin_name.lower()
    if path.basename(fsboot.executable_dir()).endswith("-private"):
        exe_file = path.join(
            fsboot.executable_dir(),
            "..",
            f"{dir_name}-private",
            get_exe_name(name),
        )

        if check_executable(exe_file):
            return exe_file
    exe_file = path.join(
        fsboot.executable_dir(), "..", dir_name, get_exe_name(name)
    )
    if check_executable(exe_file):
        return exe_file
    return None


def find_plugin_executable(name: str):
    plugin_name = known_executables.get(name)
    if plugin_name is None:
        return None
    base_dir = fsboot.base_dir()
    plugins_dir = path.join(base_dir, "System")
    exe_file = find_executable_in_plugins_dir(name, plugins_dir, plugin_name)
    if exe_file:
        return exe_file
    # plugins_dir = path.join(base_dir, "Plugins")
    # exe_file = find_executable_in_plugins_dir(name, plugins_dir, plugin_name)
    # if exe_file:
    #     return exe_file
    # plugins_dir = path.join(base_dir, "Data", "Plugins")
    # exe_file = find_executable_in_plugins_dir(name, plugins_dir, plugin_name)
    # if exe_file:
    #     return exe_file
    return None


def find_side_by_side_app_executable(name: str):
    plugin_name = known_executables.get(name)
    if plugin_name is None:
        return None
    app_name = f"{plugin_name}.app"
    bin_dir = path.join(fsboot.executable_dir(), "..", "..")
    exe_file = path.join(bin_dir, app_name, "Contents", "MacOS", name)
    if check_executable(exe_file):
        return exe_file


def find_side_by_side_plugin_executable(name: str):
    plugin_name = known_executables.get(name)
    if plugin_name is None:
        return None
    current_plugin_dir = get_current_plugin_dir()
    if current_plugin_dir is None:
        print("Is not running in a plugin")
        return None
    plugins_dir = path.join(current_plugin_dir, "..")
    return find_executable_in_plugins_dir(name, plugins_dir, plugin_name)


def find_executable_in_plugins_dir(
    name: str, plugins_dir: str, plugin_name: str
):
    bin_dir = path.join(plugins_dir, plugin_name, os_name(), arch_name())
    return find_executable_in_dir_or_app(name, bin_dir, name)


def find_executable_in_dir_or_app(name: str, bin_dir: str, plugin_name: str):
    print("find_executable_in_dir_or_app", name, bin_dir)
    ext = ".exe" if System.windows else ""
    exe_name = f"{name}{ext}"
    exe_file = path.join(bin_dir, exe_name)
    if check_executable(exe_file):
        return exe_file
    if System.macos:
        app_name = f"{plugin_name}.app"
        exe_file = path.join(bin_dir, app_name, "Contents", "MacOS", exe_name)
        if check_executable(exe_file):
            return exe_file
    return None


def find_side_by_side_executable(name: str):
    """Find executable side by side, for example in /usr/bin or similar."""
    exe_file = path.join(fsboot.executable_dir(), name)
    if check_executable(exe_file):
        return exe_file


def get_exe_name(name: str) -> str:
    if System.windows:
        return f"{name}.exe"
    return name


def os_name() -> str:
    if System.windows:
        return "Windows"
    elif System.macos:
        return "macOS"
    elif System.linux:
        return "Linux"
    else:
        return "Other"


def arch_name() -> str:
    if platform.machine().lower() in X86_ANY_MACHINES:
        if platform.architecture()[0] == "64bit":
            return "x86-64"
        else:
            return "x86"
    return "Unknown"


def check_executable(exe_file: str) -> bool:
    if path.exists(exe_file):
        print(f"Check executable {exe_file}: YES")
        return True
    else:
        print(f"Check executable {exe_file}: NO")
        return False
