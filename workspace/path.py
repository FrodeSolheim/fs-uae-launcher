import logging
import os

import fsboot

logger = logging.getLogger("WORKSPACE")
assigns = {
    "C": "Workspace:C",
    # "CLIPS": "Ram Disk:Clipboards",
    "DEVS": "Workspace:Devs",
    "ENV": "Ram Disk:ENV",
    "ENVARC": "Workspace:Prefs/Env-Archive",
    "FONTS": "Workspace:Fonts",
    "HELP": "Workspace:Locale/Help",
    # "KEYMAPS": "Workspace:Devs/Keymaps",
    # "L": "Workspace:L",
    "LIBS": "Workspace:Libs",
    "LOCALE": "Workspace:Locale",
    # "PRINTERS": "Workspace:Devs/Printers",
    "REXX": "Workspace:S",
    "S": "Workspace:S",
    "SYS": "Workspace:",
    # "T": "Ram Disk:T",
    # FIXME: Perhaps
    "CDROMS": "Media/CD-ROMs",
    "DISKS": "Media/Hard Drives",
    "FLOPPIES": "Media/Floppies",
    "ICONS": "Workspace:FIXME/Icons",
    "LOGS": "Ram Disk:T/Logs",
    # "DATABASES": "Data/Databases",
    # Special
    "VOLUMES": ".",
}


def expand_assigns(path):
    logger.debug("expand_assigns %s", repr(path))
    volume, p = path.split(":")
    try:
        dir = assigns[volume]
        if not dir.endswith(":"):
            dir += "/"
        return dir + p
    except KeyError:
        return path


def basename(path):
    if "/" in path:
        return path.rsplit("/", 1)[1]
    if ":" in path:
        return path.rsplit(":", 1)[1]
    return path


def extension(path, prefix=False, suffix=True):
    name = basename(path)
    ext = ""
    name = name.lower()
    if suffix:
        ext_2 = os.path.splitext(name)[1]
        if ext_2:
            assert ext_2[0] == "."
            ext = ext_2[1:]
    if prefix:
        if name.startswith("mod."):
            ext = "mod"
    return ext


def exists(path):
    return os.path.exists(host(path))


def host(path):
    path = expand_assigns(path)
    # FIXME: make absolute
    path = path.replace("AmigaForever:", "AmigaForever/")
    path = path.replace("AmigaOS4.1:", "AmigaOS4.1/")
    path = path.replace("AmiKit:", "AmiKit/")
    path = path.replace("ClassicWB:", "ClassicWB/")
    path = path.replace("Data:", "Data/")
    path = path.replace("Games:", "Games/")
    path = path.replace("Media:", "Media/")
    path = path.replace("Ram Disk:", "Ram Disk/")
    path = path.replace("Shared:", "Shared/")
    path = path.replace("Systems:", "Systems/")
    path = path.replace("Workspace:", "Workspace/")
    if not os.path.isabs(path):
        path = os.path.join(fsboot.base_dir(), path)
    return path


def listdir(path):
    host_path = host(path)
    items = os.listdir(host_path)
    if path == "VOLUMES:":
        items = [x for x in items if os.path.isdir(os.path.join(host_path, x))]
        if "Cache" in items:
            items.remove("Cache")
        if "Floppies" in items:
            items.remove("Floppies")
        if "CD-ROMs" in items:
            items.remove("CD-ROMs")
        if "Hard Drives" in items:
            items.remove("Hard Drives")
        if "Kickstarts" in items:
            items.remove("Kickstarts")
        if "Save States" in items:
            items.remove("Save States")
        if "Controllers" in items:
            items.remove("Controllers")
        if "Source" in items:
            items.remove("Source")
        if "Themes" in items:
            items.remove("Themes")
        if "Configurations" in items:
            items.remove("Configurations")
    return items


def isdir(path):
    logger.debug("workspace.path.isdir %s", repr(path))
    return os.path.isdir(host(path))


def join(a, b, *args):
    if a == "VOLUMES:":
        return b + ":"
    path = a
    if not a.endswith(":"):
        path += "/"
    path += b
    for arg in args:
        path += "/" + arg
    return path


class Path:
    def __init__(self, path):
        self._path = path

    def host(self):
        return host(self._path)
