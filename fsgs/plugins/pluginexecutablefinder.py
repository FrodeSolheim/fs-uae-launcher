import platform
from os import path

import fsboot
from fsbc.system import System

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
        print("Find executable:", name)
        exe_file = find_executable(name)
        if exe_file:
            exe_file = path.normpath(exe_file)
            print("->", exe_file)
            return exe_file
        print("-> None")
        return None


def find_executable(name: str):
    if fsboot.development():
        exe_file = find_executable_in_development_project_dir(name)
        if exe_file:
            return exe_file
    exe_file = find_executable_in_plugins_dir(name)
    if exe_file:
        return exe_file
    if System.macos and fsboot.is_frozen():
        exe_file = find_executable_in_side_by_side_app_bundle(name)
        if exe_file:
            return exe_file
    exe_file = find_executable_side_by_side(name)
    if exe_file:
        return exe_file
    exe_file = find_executable_in_side_by_side_plugin(name)
    if exe_file:
        return exe_file
    return None


def find_executable_in_development_project_dir(name: str):
    print("- Find executable in development project dir")
    plugin_name = known_executables.get(name)
    if plugin_name is None:
        return None
    project_dir_name = plugin_name.lower()
    exe_dir = fsboot.executable_dir()
    if exe_dir.endswith("-private"):
        exe_file = path.join(
            exe_dir,
            "..",
            f"{project_dir_name}-private",
            get_exe_name(name),
        )
        if check_executable(exe_file):
            return exe_file
        if project_dir_name == "fs-uae":
            exe_file = path.join(
                exe_dir,
                "..",
                "fs-uae-3-private",
                get_exe_name(name),
            )
            if check_executable(exe_file):
                return exe_file
    exe_file = path.join(exe_dir, "..", project_dir_name, get_exe_name(name))
    if check_executable(exe_file):
        return exe_file
    return None


def find_executable_in_plugins_dir(name: str):
    print("- Find executable in plugins dir")
    plugin_name = known_executables.get(name)
    if plugin_name is None:
        return None
    base_dir = fsboot.base_dir()
    plugins_dir = path.join(base_dir, "System")
    exe_file = find_executable_in_dir_containing_plugin(
        name, plugins_dir, plugin_name
    )
    if exe_file:
        return exe_file
    print("  Looking in legacy plugin directories")
    plugins_dir = path.join(base_dir, "Plugins")
    exe_file = find_executable_in_dir_containing_plugin(
        name, plugins_dir, plugin_name
    )
    if exe_file:
        return exe_file
    plugins_dir = path.join(base_dir, "Data", "Plugins")
    exe_file = find_executable_in_dir_containing_plugin(
        name, plugins_dir, plugin_name
    )
    if exe_file:
        return exe_file
    return None


def find_executable_in_side_by_side_app_bundle(name: str):
    print("- Find executable in side-by-side app bundle")
    plugin_name = known_executables.get(name)
    if plugin_name is None:
        return None
    exe_file = path.join(
        fsboot.app_dir(), f"{plugin_name}.app", "Contents", "MacOS", name
    )
    if check_executable(exe_file):
        return exe_file


def find_executable_in_side_by_side_plugin(name: str):
    print("- Find executable in side-by-side plugin")
    plugin_name = known_executables.get(name)
    if plugin_name is None:
        return None
    # plugin_dir = fsboot.plugin_dir()
    # if plugin_dir is None:
    #     print("  Not running in a plugin")
    #     return None
    # plugins_dir = path.join(plugin_dir, "..")
    plugins_dir = path.join(fsboot.app_dir(), "..", "..", "..")
    return find_executable_in_dir_containing_plugin(
        name, plugins_dir, plugin_name
    )


def find_executable_in_dir_containing_plugin(
    name: str, plugins_dir: str, plugin_name: str
):
    bin_dir = path.join(plugins_dir, plugin_name, os_name(), arch_name())
    return find_executable_in_dir_or_app(name, bin_dir, plugin_name)


def find_executable_in_dir_or_app(name: str, dir: str, plugin_name: str):
    if System.macos:
        exe_file = path.join(
            dir, f"{plugin_name}.app", "Contents", "MacOS", name
        )
        if check_executable(exe_file):
            return exe_file
    else:
        exe_file = path.join(dir, get_exe_name(name))
        if check_executable(exe_file):
            return exe_file
    return None


def find_executable_side_by_side(name: str):
    """Find executable side by side, for example in /usr/bin or similar."""
    print("- Find executable side-by-side")
    exe_file = path.join(fsboot.executable_dir(), get_exe_name(name))
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
    # FIXME: arm7/8 and ARM64
    return "Unknown"


def check_executable(exe_file: str) -> bool:
    if path.exists(exe_file):
        print(f"  Check executable {exe_file}: YES")
        return True
    else:
        print(f"  Check executable {exe_file}: NO")
        return False
