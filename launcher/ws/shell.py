import os

from fsgamesys.directories import temp_directory
from fsgamesys.FSGSDirectories import FSGSDirectories
from fsgamesys.product import Product
from launcher.ws.shellicon import ShellIcon

trace = True


# class Shell:
#     pass


def shell_basename(path):
    return shell_split(path)[1]


def shell_dirname(path):
    return shell_split(path)[0]


def shell_hostpath(path):
    if not path:
        return ""
    parts = shell_splitfull(path)
    volume = parts[0].lower()
    if volume == "system:":
        pass
    else:
        volume_dir = volume_host_path(volume)
        if volume_dir:
            path_realcase = shell_realcase(path)
            real_path = os.path.join(volume_dir, path_realcase[len(volume) :])
            return real_path
    raise Exception("Cannot convert to real path")


def shell_icon(path):
    return ShellIcon(shell_hostpath(path))


def shell_icons(path):
    pass


def entries(obj):
    if callable(obj["entries"]):
        return obj["entries"]()
    return obj["entries"]


def shell_isdir(path):
    """
    >>> shell_isdir('System:')
    True
    """
    if not path:
        return False
    parts = shell_splitfull(path)
    volume = parts[0].lower()
    if volume == "system:":
        obj = vfs
        for part in parts:
            part = part.lower()
            try:
                obj = entries(obj)[part]
            except KeyError:
                return False
        return "entries" in obj
    else:
        volume_dir = volume_host_path(volume)
        if volume_dir:
            path_realcase = shell_realcase(path)
            real_path = os.path.join(volume_dir, path_realcase[len(volume) :])
            return os.path.isdir(real_path)
    return False


def shell_listdir(path):
    if trace:
        print("shell_listdir", path)
    parts = shell_splitfull(path)
    volume = parts[0].lower()
    if volume == "system:":
        obj = vfs
        for part in parts:
            part = part.lower()
            obj = entries(obj)[part]
        result = [entry["name"] for entry in entries(obj).values()]
        return list(sorted(result))
    else:
        volume_dir = volume_host_path(volume)
        if volume_dir:
            path_realcase = shell_realcase(path)
            real_path = os.path.join(volume_dir, path_realcase[len(volume) :])
            return sorted(os.listdir(real_path))
    # FIXME: Custom exception? Or some IOError?
    raise LookupError("No such directory")


def shell_join(path, *names):
    """
    >>> shell_join('System:', 'Prefs')
    'System:Prefs'
    >>> shell_join('Prefs', 'Env-Archive')
    'Prefs/Env-Archive'
    >>> shell_join('System:', 'Prefs', 'Env-Archive')
    'System:Prefs/Env-Archive'
    """
    result = [path]
    for name in names:
        if not (len(result) == 1 and result[0].endswith(":")):
            result.append("/")
        result.append(name)
    return "".join(result)


def shell_name(path):
    # FIXME: Return non-lowercase name
    name = shell_basename(path)
    if name.endswith(":"):
        name = name[:-1]
    return name


def shell_normcase(path):
    return path.lower()


# def shell_normpath(path):
#     return


# def os_realcase(path):
#     result = []
#     while True:
#         path, basename = os.path.split(path)
#         if basename == "":
#             break
#         basename_lower = basename.lower()
#         items = os.listdir(path)
#         for item in items:
#             if item.lower() == basename_lower:
#                 result.append(item)
#                 break
#         else:
#             raise LookupError(f"Could not find case for {basename} in {path}")
#     return reversed(result)


def shell_realcase(path):
    print("shell_realcase", path)
    result = []
    parts = shell_splitfull(path)
    volume = parts[0].lower()
    if volume == "system:":
        obj = vfs
        for i, part in enumerate(parts):
            if i >= 2:
                result.append("/")
            part = part.lower()
            try:
                obj = entries(obj)[part]
            except KeyError:
                return None
            result.append(obj["name"])
        # if "size" in obj:
        #     return (None, (obj["size"]["width"], obj["size"]["height"]))
        # return (None, None)
    else:
        volume_dir = volume_host_path(volume)
        if volume_dir:
            print("volume_dir", volume_dir)
            # FIXME: Case handling...
            # if volume == "data:":
            #     result.append("Data:")
            # elif volume == "whdload:":
            #     result.append("WHDLoad:")
            # else:
            #     raise Exception("FIXME")

            for shellvolume in shell_volumes():
                if shellvolume.lower() == volume:
                    result.append(shellvolume)
                    break
            else:
                raise Exception(f"Could not find case for volume {volume}")

            path = volume_dir
            parts = parts[1:]
            for part in parts:
                part_lower = part.lower()
                print(path)
                items = os.listdir(path)
                for item in items:
                    if item.lower() == part_lower:
                        if len(result) > 1:
                            result.append("/")
                        result.append(item)
                        path = os.path.join(path, item)
                        break
                else:
                    raise LookupError(
                        f"Could not find case for {part} in {path}"
                    )
        else:
            raise LookupError("Path not found")
    print(result)
    return "".join(result)


def shell_split(path):
    """
    >>> shell_split('System:Prefs')
    ('System:', 'Prefs')
    >>> shell_split('Prefs/Env-Archive')
    ('Prefs', 'Env-Archive')
    >>> shell_split('System:Prefs/Env-Archive')
    ('System:Prefs', 'Env-Archive')
    """
    if not path:
        return "", ""
    try:
        head, tail = path.rsplit("/", 1)
    except ValueError:
        try:
            head, tail = path.split(":", 1)
            if tail:
                head = head + ":"
            else:
                tail = head + ":"
                head = ""
        except ValueError:
            head = ""
            tail = path
    return head, tail


def shell_splitfull(path):
    """
    >>> shell_splitfull('System:Prefs')
    ['System:', 'Prefs']
    >>> shell_splitfull('Prefs/Env-Archive')
    ['Prefs', 'Env-Archive']
    >>> shell_splitfull('System:Prefs/Env-Archive')
    ['System:', 'Prefs', 'Env-Archive']
    """
    result = []
    dirname, basename = shell_split(path)
    result.append(basename)
    while dirname:
        # print(dirname)
        dirname, basename = shell_split(dirname)
        result.append(basename)
    return list(reversed(result))


def shell_volumes():
    return [
        "Ram Disk:",
        "System:",
        "Data:",
        "Media:",
        # "Games:",
        # "Media:",
        "Shared:",
        # "Software:",
        # "WHDLoad:",
        # "Work:",
        "AmigaForever:",
    ]


def shell_window_geometry(path):
    parts = shell_splitfull(path)
    obj = vfs
    for part in parts:
        part = part.lower()
        try:
            obj = entries(obj)[part]
        except KeyError:
            return (None, None)
    if "size" in obj:
        return (None, (obj["size"]["width"], obj["size"]["height"]))
    return (None, None)


def volume_host_path(volume):
    if volume == "data:":
        return FSGSDirectories.get_data_dir()
    elif volume == "amigaforever:":
        return os.path.join(FSGSDirectories.get_base_dir(), "AmigaForever")
    elif volume == "games:":
        return os.path.join(FSGSDirectories.get_base_dir(), "Games")
    elif volume == "media:":
        return os.path.join(FSGSDirectories.get_base_dir(), "Media")
    elif volume == "ram disk:":
        # return os.path.join(FSGSDirectories.get_base_dir(), "Cache")
        return os.path.join(temp_directory())
    elif volume == "shared:":
        # Or ...HardDrives/Shared ?
        return os.path.join(FSGSDirectories.get_base_dir(), "Shared")
    elif volume == "software:":
        return os.path.join(FSGSDirectories.get_base_dir(), "Software")
    elif volume == "whdload:":
        return os.path.join(FSGSDirectories.get_base_dir(), "WHDLoad")
    elif volume == "work:":
        return os.path.join(FSGSDirectories.get_base_dir(), "Work")
    else:
        return None


vfs_platforms = {
    "name": "Platforms",
    # ...
    "entries": {
        "amstradcpc": {
            "name": "AmstradCPC",
        },
        "amstradcpc.info": {"name": "AmstradCPC.info"},
        "arcade": {
            "name": "Arcade",
        },
        "arcade.info": {"name": "Arcade.info"},
        "atari7800": {
            "name": "Atari7800",
        },
        "atari7800.info": {"name": "Atari7800.info"},
        "atarist": {
            "name": "AtariST",
        },
        "atarist.info": {"name": "AtariST.info"},
        "commodore64": {
            "name": "Commodore64",
        },
        "commodore64.info": {"name": "Commodore64.info"},
        "dos": {
            "name": "DOS",
        },
        "dos.info": {"name": "DOS.info"},
        "gameboy": {
            "name": "GameBoy",
        },
        "gameboy.info": {"name": "GameBoy.info"},
        "gameboyadvance": {
            "name": "GameBoyAdvance",
        },
        "gameboyadvance.info": {"name": "GameBoyAdvance.info"},
        "gameboycolor": {
            "name": "GameBoyColor",
        },
        "gameboycolor.info": {"name": "GameBoyColor.info"},
        "mastersystem": {
            "name": "MasterSystem",
        },
        "mastersystem.info": {"name": "MasterSystem.info"},
        "megadrive": {
            "name": "MegaDrive",
        },
        "megadrive.info": {"name": "MegaDrive.info"},
        "neogeo": {
            "name": "Neo-Geo",
        },
        "neogeo.info": {"name": "Neo-Geo.info"},
        "nintendo": {
            "name": "Nintendo",
        },
        "nintendo.info": {"name": "Nintendo.info"},
        "playstation": {
            "name": "PlayStation",
        },
        "playstation.info": {"name": "PlayStation.info"},
        "supernintendo": {
            "name": "SuperNintendo",
        },
        "supernintendo.info": {"name": "SuperNintendo.info"},
        "turbografx-16": {
            "name": "TurboGrafx-16",
        },
        "turbografx-16.info": {"name": "TurboGrafx-16.info"},
        "turbografx-cd": {
            "name": "TurboGrafx-CD",
        },
        "turbografx-cd.info": {"name": "TurboGrafx-CD.info"},
        "zxspectrum": {
            "name": "ZXSpectrum",
        },
        "zxspectrum.info": {"name": "ZXSpectrum.info"},
    },
}


def vfs_prefs_entries():
    result = {
        "advanced": {
            "name": "Advanced",
        },
        "advanced.info": {"name": "Advanced.info"},
        "privacy": {
            "name": "Privacy",
        },
        "privacy.info": {"name": "Privacy.info"},
    }
    if Product.is_fs_uae():
        result.update(
            {
                # # self.iconview.add_icon(label="Input")
                # # FIXME: Should be a tool or utility instead?
                # # self.iconview.add_icon(label="Janitor")
                "appearance": {
                    "name": "Appearance",
                },
                "appearance.info": {"name": "Appearance.info"},
                "arcade": {
                    "name": "Arcade",
                },
                "arcade.info": {"name": "Arcade.info"},
                # "backup": {"name": "Backup",},
                # "backup.info": {"name": "Backup.info"},
                "controller": {
                    "name": "Controller",
                },
                "controller.info": {"name": "Controller.info"},
                # "directory": {"name": "Directory",},
                # "directory.info": {"name": "Directory.info"},
                "filedatabase": {
                    "name": "FileDatabase",
                },
                "filedatabase.info": {"name": "FileDatabase.info"},
                # "firmware": {"name": "Firmware",},
                # "firmware.info": {"name": "Firmware.info"},
                # "font": {"name": "Font",},
                # "font.info": {"name": "Font.info"},
                "gamedatabase": {
                    "name": "GameDatabase",
                },
                "gamedatabase.info": {"name": "GameDatabase.info"},
                "keyboard": {
                    "name": "Keyboard",
                },
                "keyboard.info": {"name": "Keyboard.info"},
                "locale": {
                    "name": "Locale",
                },
                "locale.info": {"name": "Locale.info"},
                "logging": {
                    "name": "Logging",
                },
                "logging.info": {"name": "Logging.info"},
                "midi": {
                    "name": "MIDI",
                },
                "midi.info": {"name": "MIDI.info"},
                "mouse": {
                    "name": "Mouse",
                },
                "mouse.info": {"name": "Mouse.info"},
                # "netplay": {"name": "NetPlay",},
                # "netplay.info": {"name": "NetPlay.info"},
                "opengl": {
                    "name": "OpenGL",
                },
                "opengl.info": {"name": "OpenGL.info"},
                "openretro": {
                    "name": "OpenRetro",
                },
                "openretro.info": {"name": "OpenRetro.info"},
                # "overscan": {"name": "Overscan",},
                # "overscan.info": {"name": "Overscan.info"},
                "platforms": vfs_platforms,
                "platforms.info": {"name": "Platforms.info"},
                "plugin": {
                    "name": "Plugin",
                },
                "plugin.info": {"name": "Plugin.info"},
                "power": {
                    "name": "Power",
                },
                "power.info": {"name": "Power.info"},
                "screenmode": {
                    "name": "ScreenMode",
                },
                "screenmode.info": {"name": "ScreenMode.info"},
                "sound": {
                    "name": "Sound",
                },
                "sound.info": {"name": "Sound.info"},
                "storage": {
                    "name": "Storage",
                },
                "storage.info": {"name": "Storage.info"},
                "video": {
                    "name": "Video",
                },
                "video.info": {"name": "Video.info"},
                "whdload": {
                    "name": "WHDLoad",
                },
                "whdload.info": {"name": "WHDLoad.info"},
                "workspace": {
                    "name": "Workspace",
                },
                "workspace.info": {"name": "Workspace.info"},
            }
        )
    return result


vfs_prefs = {
    "name": "Prefs",
    # ...
    "entries": vfs_prefs_entries,
}

vfs_tools = {
    "name": "Tools",
    "size": {"width": 400, "height": 300},
    # ...
    "entries": {
        "calculator": {
            "name": "Calculator",
        },
        "calculator.info": {"name": "Calculator.info"},
        "databaseupdater": {
            "name": "DatabaseUpdater",
        },
        "databaseupdater.info": {"name": "DatabaseUpdater.info"},
        "filescanner": {
            "name": "FileScanner",
        },
        "filescanner.info": {"name": "FileScanner.info"},
    },
}

vfs_utilities = {
    "name": "Utilities",
    "size": {"width": 400, "height": 200},
    # ...
    "entries": {
        "checksum": {
            "name": "Checksum",
        },
        "checksum.info": {"name": "Checksum.info"},
        "clock": {
            "name": "Clock",
        },
        "clock.info": {"name": "Clock.info"},
        "multiview": {
            "name": "MultiView",
        },
        "multiview.info": {"name": "MultiView.info"},
    },
}

vfs_system = {
    "name": "System:",
    "size": {"width": 600, "height": 300},
    "entries": {
        "arcade": {
            "name": "Arcade",
        },
        "arcade.info": {"name": "Arcade.info"},
        "launcher": {
            "name": "Launcher",
        },
        "launcher.info": {"name": "Launcher.info"},
        "prefs": vfs_prefs,
        "prefs.info": {"name": "Prefs.info"},
        "tools": vfs_tools,
        "tools.info": {"name": "Tools.info"},
        "utilities": vfs_utilities,
        "utilities.info": {"name": "Utilities.info"},
    },
}

vfs = {
    "name": "Root",
    # ...
    "entries": {
        # ...
        "system:": vfs_system,
    },
}

if __name__ == "__main__":
    import doctest

    doctest.testmod()
