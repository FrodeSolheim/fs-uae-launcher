from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import fsui

volumes = None


def get_vfs_volumes():
    global volumes
    if volumes is None:
        volumes = []
        volumes.append(BuiltinItem(
            "Workspace", "Workspace:", default_items["Workspace"]))
    return volumes[:]


def get_vfs_item(uri):
    volume_name, path = uri.split(":")
    for volume in get_vfs_volumes():
        if not volume.name() == volume_name:
            continue
        item = volume
        break
    else:
        return None
    parts = path.split("/")
    for part in parts:
        item = item.item(part)
    return item


class VFSIcon(object):
    pass


class VFSKnownIcon(VFSIcon):

    def __init__(self, name):
        self.name = name

    def image(self):
        return fsui.Image("fs_uae_workspace:res/48/" + self.name + ".png")


class VFSNoIcon(VFSKnownIcon):

    __instance = None

    @classmethod
    def instance(cls):
        if cls.__instance is None:
            cls.__instance = VFSNoIcon("no_icon")
        return cls.__instance


class VFSItem(object):

    def __init__(self, uri):
        self._uri = uri

    def icon(self):
        return VFSNoIcon.instance()

    def children(self):
        return []

    def uri(self):
        return self._uri

    def item(self, name):
        raise KeyError(name)

    def name(self):
        raise NotImplementedError()

    def display_name(self):
        return self.name()

    # def open(self, mode):
    #     raise NotImplementedError()


class VFSVolume(VFSItem):
    pass


class BuiltinItem(VFSItem):

    def __init__(self, name, uri, node):
        self._name = name
        self._uri = uri
        self._node = node

    def name(self):
        return self._name

    def open(self, args=[]):
        if "app" in self._node:
            _temp = __import__(self._node["app"], globals(), locals(),
                               ["application"])
            application = _temp.application(self.uri(), args)

    def content_type(self):
        if "app" in self._node:
            return "application/x-fs-uae-application"
        else:
            return "application/x-fs-uae-vfolder"

    def uri(self):
        return self._uri

    def icon(self):
        return VFSKnownIcon(self._node["icon"])

    def children(self):
        return [x for x in self._node["children"]]

    def item(self, name):
        uri = self.uri()
        if uri.endswith(":"):
            uri = self._uri + name
        else:
            uri = self._uri + "/" + name
        return BuiltinItem(name, uri, self._node["children"][name])


class VFSDesktopItem(VFSItem):

    def __init__(self):
        self._items = {}
        # self._items["FS-UAE (Old)"] = FSUAEVolume()

        self._items["Workspace"] = BuiltinItem(
            "Workspace", "Workspace:", default_items["Workspace"])
        self._items["Files"] = BuiltinItem(
            "Files", "Files:", default_items["Files"])
        self._items["Ubuntu"] = BuiltinItem(
            "Ubuntu", "Ubuntu:", default_items["Ubuntu"])

        self._items["Clock"] = BuiltinItem(
            "Clock", "Workspace:Utilities/Clock",
                    default_items["Workspace"]["children"]["Utilities"][
                        "children"]["Clock"])
        self._items["Language"] = BuiltinItem(
            "Language", "Workspace:Utilities/Language",
                    default_items["Workspace"]["children"]["Prefs"][
                        "children"]["Language"])

        self._items["ADFCreator"] = BuiltinItem(
            "Language", "Workspace:Tools/ADFCreator",
                    default_items["Workspace"]["children"]["Tools"][
                        "children"]["ADFCreator"])
        self._items["HDFCreator"] = BuiltinItem(
            "Language", "Workspace:Tools/HDFCreator",
                    default_items["Workspace"]["children"]["Tools"][
                        "children"]["HDFCreator"])

        # self._items["Floppies"] = FloppiesVolume()
        # self._items["Configs"] = ConfigsVolume()

    def name(self):
        return "FS-UAE Workbench"

    # def icon(self):
    #     return VFSKnownIcon("fs-uae")

    def children(self):
        return self._items.keys()

    def item(self, name):
        return self._items[name]


class FileSystemDirectory(VFSItem):

    def __init__(self, uri, path):
        pass


class FileSystemVolume(FileSystemDirectory):

    def __init__(self, uri, name, path):
        pass


class FSUAEPreferences(VFSItem):

    def icon(self):
        return VFSKnownIcon("preferences")


class FSUAETools(VFSItem):

    def icon(self):
        return VFSKnownIcon("tools")


class FSUAELauncher(VFSItem):

    def icon(self):
        return VFSKnownIcon("fs-uae-launcher")


class FSUAEPlugins(VFSItem):

    def icon(self):
        return VFSKnownIcon("folder-plugins")


class FSUAEGameCenter(VFSItem):

    def icon(self):
        return VFSKnownIcon("arcade")


class FSUAENetplay(VFSItem):

    def icon(self):
        return VFSKnownIcon("netplay")


class FSUAEAmiga(VFSItem):

    def icon(self):
        return VFSKnownIcon("amiga-computer")


class FSUAEKickstarts(VFSItem):

    def icon(self):
        return VFSKnownIcon("kickstarts")


class FSUAEConfigs(VFSItem):

    def icon(self):
        return VFSKnownIcon("folder")


class FSUAEVolume(VFSItem):

    _item_map = {
        "Preferences": FSUAEPreferences,
        "Tools": FSUAETools,
        "Launcher": FSUAELauncher,
        "Plugins": FSUAEPlugins,
        "Arcade": FSUAEGameCenter,
        "Netplay": FSUAENetplay,
        "Models": FSUAEAmiga,
        "Kickstarts": FSUAEKickstarts,
        "Configs": FSUAEConfigs,
    }

    def __init__(self):
        VFSItem.__init__(self, "FS-UAEOld:")

    def name(self):
        return "FS-UAE"

    def icon(self):
        return VFSKnownIcon("fs-uae-volume")

    def children(self):
        return self._item_map.keys()

    def item(self, name):
        item_uri = self.uri() + name
        return self._item_map[name](item_uri)


class FloppiesVolume(VFSItem):

    def __init__(self):
        VFSItem.__init__(self, "Floppies:")

    def name(self):
        return "Floppies"

    def icon(self):
        return VFSKnownIcon("floppies-volume")

    def children(self):
        return []


class ConfigsVolume(VFSItem):

    def __init__(self):
        VFSItem.__init__(self, "Configs:")

    def name(self):
        return "Configs"

    def icon(self):
        return VFSKnownIcon("configs-volume")

    def children(self):
        return []


default_items = {
    "Workspace": {
        "icon": "fs-uae-volume",
        "children": {
            "Arcade": {
                "icon": "arcade",
                "app": "fs_uae_workspace.apps.arcade_app",
            },
            "Launcher": {
                "icon": "fs-uae-launcher",
                "app": "fs_uae_workspace.apps.launcher_app",
            },
            "Netplay": {
                "icon": "netplay",
                "app": "fs_uae_workspace.apps.netplay_app",
            },
            "Plugins": {
                "icon": "plugins-folder",
            },
            "Prefs": {
                "icon": "preferences",
                "children": {
                    "Audio": {
                        "icon": "audio-settings",
                        "app": "fs_uae_workspace.prefs.audio",
                    },
                    "Experimental": {
                        "icon": "settings",
                        "app": "fs_uae_workspace.prefs.experimental_features",
                    },
                    "Filters": {
                        "icon": "filter-settings",
                        "app": "fs_uae_workspace.prefs.filter",
                    },
                    "GameDB": {
                        "icon": "database-settings",
                        "app": "fs_uae_workspace.prefs.game_database",
                    },
                    "Keyboard": {
                        "icon": "keyboard-settings",
                        "app": "fs_uae_workspace.prefs.keyboard",
                    },
                    "Joysticks": {
                        "icon": "joystick-settings",
                        "app": "fs_uae_workspace.prefs.joystick",
                    },
                    "Language": {
                        "icon": "language-settings",
                        "app": "fs_uae_workspace.prefs.language",
                    },
                    "Mice": {
                        "icon": "mouse-settings",
                        "app": "fs_uae_workspace.prefs.mouse",
                    },
                    "Netplay": {
                        "icon": "netplay-settings",
                        "app": "fs_uae_workspace.prefs.netplay",
                    },
                    # "OpenGL": {
                    #     "icon": "setting",
                    #     "app": "fs_uae_workspace.prefs.opengl",
                    # },
                    "Scan": {
                        "icon": "indexing-settings",
                        "app": "fs_uae_workspace.prefs.scan",
                    },
                    "User": {
                        "icon": "preferences",
                        "children": {
                            "Login": {
                                "icon": "preferences",
                                "app": "fs_uae_workspace.apps.login",
                            },
                            "Logout": {
                                "icon": "preferences",
                                "app": "fs_uae_workspace.apps.logout",
                            },
                        },
                    },
                    "Video": {
                        "icon": "video-settings",
                        "app": "fs_uae_workspace.prefs.video",
                    },
                },
            },
            "Tools": {
                "icon": "tools",
                "children": {
                    "ADFCreator": {
                        "icon": "floppy",
                        "app": "fs_uae_workspace.apps.adf_creator_app",
                    },
                    "Calculator": {
                        "icon": "calculator",
                        "app": "fs_uae_workspace.apps.calculator_app",
                    },
                    "HDFCreator": {
                        "icon": "volume",
                        "app": "fs_uae_workspace.apps.hdf_creator_app",
                    },
                    "KeyShow": {
                        "icon": "key-map",
                        "app": "fs_uae_workspace.apps.key_show_app",
                    },
                    "LogViewer": {
                        "icon": "log-viewer",
                        "app": "fs_uae_workspace.apps.logviewer_app",
                    },
                    "TOSECOrganizer": {
                        "icon": "file-manager",
                        "app": "fs_uae_workspace.apps.tosec_organizer_app",
                    },
                    "JoystickConfig": {
                        "icon": "settings",
                        "app": "fs_uae_workspace.apps.joystick_config_app",
                    },
                    "Refresh": {
                        "icon": "settings",
                        "app": "fs_uae_workspace.apps.refresh",
                    },
                    "LockerUploader": {
                        "icon": "settings",
                        "app": "fs_uae_workspace.apps.locker_uploader",
                    },
                },
            },
            "Utilities": {
                "icon": "utilities",
                "children": {
                    "Clock": {
                        "icon": "clock",
                        "app": "fs_uae_workspace.apps.clock_app",
                    },
                },
            },
        },
    },
    "Files": {
        "icon": "volume",
        "children": {
        },
    },
    "Ubuntu": {
        "icon": "ubuntu-volume",
        "children": {
        },
    },
}
