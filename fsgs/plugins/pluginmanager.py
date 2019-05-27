import logging
import os
import platform
import subprocess
import traceback
from configparser import ConfigParser, NoSectionError
from operator import attrgetter

import fsboot
from fsbc.util import Version

from fsbc.system import System, windows, linux
from fsgs.FSGSDirectories import FSGSDirectories

X86_MACHINES = ["x86", "i386", "i486", "i586", "i686"]
X86_64_MACHINES = ["x86_64", "x86-64", "amd64"]
X86_ANY_MACHINES = X86_MACHINES + X86_64_MACHINES

logger = logging.getLogger("PLUGINS")

known_plugin_versions = {
    "CAPSImg": "5.1fs3",
    "Cheats": "1.0.0",
    "DOSBox-FS": "0.74.4006fs7",
    "Fuse-FS": "1.3.3fs5",
    "GenesisPlusGX-LR": "1.7.4git",
    "Hatari-FS": "2.0.0fs1",
    "MAME-FS": "0.189fs1",
    "Mednafen-FS": "1.22.2fs0",
    "Mupen64Plus-LR": "2.5fs0git",
    "Nestopia-LR": "1.49fs0wip",
    "QEMU-UAE": "3.8.2qemu2.2.0",
    "Regina-FS": "3.9.1fs0",
    "RetroArch-FS": "1.6.7fs1",
    "UADE-FS": "2.13fs1",
    "Vice-FS": "3.3fs0",
}


class BasePlugin:
    def __init__(self, path, name, version="0.0.0"):
        self.path = path
        self.name = name
        self.version = version
        self._provides = {}
        # outdated being None implies that it is unknown
        self.outdated = None
        known_version = known_plugin_versions.get(self.name, None)
        if known_version:
            try:
                self.outdated = Version(self.version) < Version(known_version)
            except ValueError:
                pass

    def add_provide(self, key, value):
        self._provides[key] = value

    def provides(self):
        return self._provides

    def data_file_path(self, name):
        return os.path.join(self.path, "Data", name)


class Plugin(BasePlugin):
    def __init__(self, path, name, version, cp):
        super().__init__(path, name, version)
        self.load_provides(cp)

    def load_provides(self, cp):
        logger.debug("loading provides for %s %s", self.path, self.platform())
        try:
            for key, value in cp.items(self.platform()):
                self._provides[key] = value
        except NoSectionError:
            pass

    def __str__(self):
        return "<Plugin {0}".format(self.path)

    @staticmethod
    def os_name(pretty=False):
        if windows:
            if pretty:
                return "Windows"
            return "windows"
        elif System.macos:
            if pretty:
                return "macOS"
            return "macos"
        elif linux:
            # if os.environ.get("STEAM_RUNTIME", ""):
            #     if pretty:
            #         return "SteamOS"
            #     return "steamos"
            # else:
            if pretty:
                return "Linux"
            return "linux"
        else:
            if pretty:
                return "Unknown"
            return "unknown"

    @staticmethod
    def arch_name(pretty=False):
        if platform.machine().lower() in X86_ANY_MACHINES:
            if platform.architecture()[0] == "64bit":
                return "x86-64"
            else:
                return "x86"
        else:
            if pretty:
                return "Unknown"
            return "unknown"

    @classmethod
    def platform(cls):
        return "{}_{}".format(cls.os_name(), cls.arch_name())


class Expansion(BasePlugin):
    def __init__(self, path, arch_path):
        name = os.path.basename(path)
        version_path = os.path.join(arch_path, "Version.txt")
        if os.path.exists(version_path):
            with open(version_path, "r", encoding="UTF-8") as f:
                version = f.read().strip()
        else:
            # version_path = os.path.join(path, "Data", "Version.txt")
            version_path = os.path.join(path, "Version.txt")
            with open(version_path, "r", encoding="UTF-8") as f:
                version = f.read().strip()
        super().__init__(path, name, version)
        self._arch_path = arch_path

    def load_provides(self):
        logger.debug("Loading provides for %s", repr(self.path))
        if os.path.exists(self._arch_path):
            self.load_arch_provides()

    def load_arch_provides(self):
        for item in os.listdir(self._arch_path):
            path = os.path.join(self._arch_path, item)
            if windows:
                if item.endswith(".exe"):
                    self.add_provide("executable:" + item[:-4].lower(), path)
                elif path.endswith(".dll"):
                    self.add_provide("library:" + item.lower()[:-4], path)
            else:
                if path.endswith(".so"):
                    self.add_provide("library:" + item.lower()[:-3], path)
                elif os.access(path, os.X_OK):
                    self.add_provide("executable:" + item.lower(), path)
            if System.macos:
                if path.endswith(".app"):
                    app_path = os.path.join(path, "Contents", "MacOS")
                    if os.path.exists(app_path):
                        for app_item in os.listdir(app_path):
                            p = os.path.join(app_path, app_item)
                            if os.access(p, os.X_OK):
                                self.add_provide(
                                    "executable:" + app_item.lower(), p
                                )

    def executable(self, name):
        path = self.provides()["executable:" + name]
        return PluginExecutable(self, path)

    def library_path(self, name):
        path = self.provides()["library:" + name]
        return path

    def __str__(self):
        return "<Expansion {0}".format(self.path)


class PluginResource:
    def __init__(self, plugin, name):
        self.plugin = plugin
        self.name = name

    @property
    def path(self):
        p = os.path.join(self.plugin.path, self.plugin.provides[self.name])
        return p


class Executable:
    def __init__(self, path):
        self.path = path

    def popen(self, args, env=None, **kwargs):
        logger.info("[EXECUTE] %s %s", self.path, repr(args))
        # logger.debug("PluginExecutable.popen %s %s %s",
        #              repr(args), repr(env), repr(kwargs))
        args = [self.path] + args
        if os.environ.get("FSGS_STRACE", "") == "1":
            args.insert(0, "strace")
        if env:
            env = env.copy()
        else:
            env = os.environ.copy()

        if os.environ.get("FS_PLUGINS_LD_LIBRARY_PATH") == "1":
            env["LD_LIBRARY_PATH"] = os.path.dirname(self.path)

        return subprocess.Popen(args, env=env, **kwargs)


class PluginExecutable(Executable):
    def __init__(self, plugin, path):
        super().__init__(path)
        self.plugin = plugin


class PluginManager:
    @classmethod
    def instance(cls):
        if not hasattr(cls, "_instance") or cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def plugin_path(cls):
        result = []
        plugins_dir = FSGSDirectories.get_plugins_dir()
        if plugins_dir and os.path.isdir(plugins_dir):
            result.append(plugins_dir)
        expansion_dir = os.path.join(
            FSGSDirectories.get_base_dir(), "Workspace", "Expansion"
        )
        if expansion_dir and os.path.isdir(expansion_dir):
            result.append(expansion_dir)
        if System.macos:
            system_plugins_dir = os.path.join(
                fsboot.executable_dir(),
                "..",
                "..",
                "..",
                "..",
                "..",
                "..",
                "Plugins",
            )
        else:
            system_plugins_dir = os.path.join(
                fsboot.executable_dir(), "..", "..", "..", "Plugins"
            )
        if os.path.isdir(system_plugins_dir):
            result.append(system_plugins_dir)
        return result

    def __init__(self):
        self._provides = {}
        self._plugins = []
        self._plugins_map = {}
        self.load_plugins()
        for plugin in self._plugins:
            for key, value in plugin.provides().items():
                self._provides[key] = plugin

    def plugin(self, name):
        return self._plugins_map[name]

    def plugins(self):
        return self._plugins.copy()

    def provides(self):
        return self._provides.copy()

    def load_plugins(self):
        plugin_path = self.plugin_path()
        logger.info("Executable dir: %s", fsboot.executable_dir())
        logger.info("Path: %s", plugin_path)
        logger.info("Machine: %s", platform.machine().lower())
        logger.info("Architecture: %s", platform.architecture()[0])
        logger.info(
            "Plugin OS/arch: %s/%s",
            Plugin.os_name(True),
            Plugin.arch_name(True),
        )

        for dir_path in plugin_path:
            # if not os.path.isdir(dir_path):
            #     continue
            for name in os.listdir(dir_path):
                plugin_dir = os.path.join(dir_path, name)
                if not os.path.isdir(plugin_dir):
                    continue
                try:
                    plugin = self.load_plugin(plugin_dir)
                except Exception:
                    traceback.print_exc()
                    continue
                if plugin is None:
                    continue
                self._plugins.append(plugin)
                self._plugins_map[plugin.name] = plugin
            self._plugins.sort(key=attrgetter("name"))

    def load_plugin(self, plugin_dir):
        logger.info("Load plugin %s", plugin_dir)
        plugin_ini = os.path.join(plugin_dir, "plugin.ini")
        name = os.path.basename(plugin_dir).split("_")[0]
        if not os.path.exists(plugin_ini):
            return self.load_expansion(plugin_dir)
        cp = ConfigParser()
        with open(plugin_ini, "r", encoding="UTF-8") as f:
            cp.read_file(f)
        version = cp.get("plugin", "version")
        plugin = Plugin(os.path.join(plugin_dir, version), name, version, cp)
        return plugin

    def load_expansion(self, path):
        logger.info("Load expansion %s", path)
        arch_path = os.path.join(
            path, Plugin.os_name(pretty=True), Plugin.arch_name(pretty=True)
        )
        version_path = os.path.join(arch_path, "Version.txt")
        if not os.path.exists(version_path):
            # version_path = os.path.join(path, "Data", "Version.txt")
            version_path = os.path.join(path, "Version.txt")
        if not os.path.exists(version_path):
            return None
        expansion = Expansion(path, arch_path)
        expansion.load_provides()
        return expansion

    def find_resource(self, name):
        plugin = self._provides[name]
        return PluginResource(plugin, name)

    def find_executable(self, name):
        logger.debug("PluginManager.find_executable %s", repr(name))
        try:
            plugin = self.provides()["executable:" + name]
        except KeyError:
            # Did not find executable in plugin, try to find executable
            # bundled with the program.
            if windows:
                exe_name = name + ".exe"
            else:
                exe_name = name
            path = os.path.join(fsboot.executable_dir(), exe_name)
            logger.debug("Checking %s", path)
            if os.path.exists(path):
                logger.debug("Found non-plugin executable %s", path)
                return Executable(path)
            if fsboot.development():
                if name == "x64sc-fs":
                    logger.debug("Lookup hack for vice-fs/x64sc-fs")
                    name = "vice-fs"
                path = os.path.join(
                    fsboot.executable_dir(), "..", name, exe_name
                )
                logger.debug("Checking %s", path)
                if os.path.exists(path):
                    logger.debug("Found non-plugin executable %s", path)
                    return Executable(path)
            return None
        return plugin.executable(name)

    def find_library_path(self, name):
        logger.debug("PluginManager.find_library_path %s", repr(name))
        try:
            plugin = self.provides()["library:" + name]
        except KeyError:
            # Did not find module in plugin, try to find module
            # bundled with the program.
            if windows:
                module_name = name + ".dll"
            else:
                module_name = name + ".so"
            path = os.path.join(fsboot.executable_dir(), module_name)
            if os.path.exists(path):
                logger.debug("Found non-plugin module %s", path)
                return path
            return None
        return plugin.library_path(name)
