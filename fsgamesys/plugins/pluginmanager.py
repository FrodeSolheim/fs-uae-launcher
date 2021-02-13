import logging
import os
import platform
import subprocess
import traceback
from configparser import ConfigParser, NoSectionError
from operator import attrgetter

import fsboot
from fscore.system import System
from fsbc.util import Version
from fsgamesys.FSGSDirectories import FSGSDirectories

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
        self.provides = {}
        # outdated being None implies that it is unknown
        self.outdated = None
        known_version = known_plugin_versions.get(self.name, None)
        if known_version:
            try:
                self.outdated = Version(self.version) < Version(known_version)
            except ValueError:
                pass

    def add_provide(self, key, value):
        logger.debug("%s -> %s", key, value)
        self.provides[key] = value

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
        if System.windows:
            if pretty:
                return "Windows"
            return "windows"
        elif System.macos:
            if pretty:
                return "macOS"
            return "macos"
        elif System.linux:
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
    def __init__(self, path, arch_path, version=None):
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
        self.load_sha1_provides()

    def load_sha1_provides(self):
        data_dir = os.path.join(self.path, "Data")
        sha1sums_file = os.path.join(data_dir, "SHA1SUMS")
        if os.path.exists(sha1sums_file):
            with open(sha1sums_file, "r", encoding="UTF-8") as f:
                for line in f.readlines():
                    line = line.strip()
                    if not line:
                        continue
                    sha1, relative_path = line.split(" ", 1)
                    relative_path = relative_path.lstrip("*")
                    path = os.path.join(data_dir, relative_path)
                    self.add_provide("sha1:" + sha1, path)

    def load_arch_provides(self):
        for item in os.listdir(self._arch_path):
            path = os.path.join(self._arch_path, item)
            if System.windows:
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
        path = self.provides["executable:" + name]
        return PluginExecutable(self, path)

    def library_path(self, name):
        path = self.provides["library:" + name]
        return path

    def sha1_path(self, sha1):
        path = self.provides["sha1:" + sha1]
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
    def __init__(self, path, ld_library_path=False):
        self.path = path
        self.env = {}
        if ld_library_path:
            self.env["LD_LIBRARY_PATH"] = os.path.dirname(self.path)

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
        # Plugins dir location has changed, add several old and new paths here
        # to find plugins in both places (FS-UAE and OpenRetro style).

        result = []

        # $BASE/Plugins/ or $BASE/Data/Plugins/
        plugins_dir = FSGSDirectories.get_plugins_dir()
        result.append(plugins_dir)

        # $BASE/Plugins/
        plugins_dir = os.path.join(FSGSDirectories.get_base_dir(), "Plugins")
        if plugins_dir not in result:
            result.append(plugins_dir)

        # $BASE/Data/Plugins/
        plugins_dir = os.path.join(FSGSDirectories.get_data_dir(), "Plugins")
        if plugins_dir not in result:
            result.append(plugins_dir)

        # # $BASE/Workspace/Expansion/
        # plugins_dir = os.path.join(
        #     FSGSDirectories.get_base_dir(), "Workspace", "Expansion"
        # )
        # if plugins_dir and os.path.isdir(plugins_dir):
        #     result.append(plugins_dir)

        if not fsboot.development():
            if System.macos:
                escape_exe_dir = "../../../../../.."
            else:
                escape_exe_dir = "../../.."
            # FIXME: Check that this contains something known first?
            # System/
            plugins_dir = os.path.normpath(
                os.path.join(fsboot.executable_dir(), escape_exe_dir)
            )
            result.append(plugins_dir)

            # FIXME: Check that this contains something known first?
            # System/Plugins/
            plugins_dir = os.path.normpath(
                os.path.join(
                    fsboot.executable_dir(), escape_exe_dir, "Plugins"
                )
            )
            result.append(plugins_dir)

        return result

    def __init__(self):
        self._provides = {}
        self._plugins = []
        self._plugins_map = {}
        self.load_plugins()
        for plugin in self._plugins:
            for key, value in plugin.provides.items():
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

        # Reversing order so that later loaded plugins (earlier on path)
        # takes precedence.
        # for dir_path in reversed(plugin_path):
        # I guess we should sort the list by version number and only load the
        # newest plugin per name.
        for dir_path in plugin_path:
            if not os.path.isdir(dir_path):
                continue
            # logger.debug(dir_path)
            for name in os.listdir(dir_path):
                plugin_dir = os.path.join(dir_path, name)
                logger.debug(plugin_dir)
                if not os.path.isdir(plugin_dir):
                    continue
                try:
                    plugin = self.load_plugin(plugin_dir)
                except Exception:
                    logger.debug("Could not load %s", plugin_dir)
                    traceback.print_exc()
                    continue
                if plugin is None:
                    logger.debug("No plugin in %s", plugin_dir)
                    continue
                logger.debug("Found plugin in %s", plugin_dir)
                self._plugins.append(plugin)
                self._plugins_map[plugin.name] = plugin
            self._plugins.sort(key=attrgetter("name"))

    def load_plugin(self, plugin_dir):
        return self.load_expansion(plugin_dir)

        # logger.info("Load plugin %s", plugin_dir)
        # plugin_ini = os.path.join(plugin_dir, "plugin.ini")
        # name = os.path.basename(plugin_dir).split("_")[0]
        # if not os.path.exists(plugin_ini):
        #     return self.load_expansion(plugin_dir)
        # cp = ConfigParser()
        # with open(plugin_ini, "r", encoding="UTF-8") as f:
        #     cp.read_file(f)
        # version = cp.get("plugin", "version")
        # plugin = Plugin(os.path.join(plugin_dir, version), name, version, cp)
        # return plugin

    def load_expansion(self, path):
        logger.info("Load expansion %s", path)
        arch_path = os.path.join(
            path, Plugin.os_name(pretty=True), Plugin.arch_name(pretty=True)
        )
        version_path = os.path.join(arch_path, "Version.txt")
        if not os.path.exists(version_path):
            # version_path = os.path.join(path, "Data", "Version.txt")
            version_path = os.path.join(path, "Version.txt")

        version = None
        if not os.path.exists(version_path):
            plugin_ini = os.path.join(path, "Plugin.ini")
            if os.path.exists(plugin_ini):
                cp = ConfigParser()
                with open(plugin_ini, "r", encoding="UTF-8") as f:
                    cp.read_file(f)
                version = cp.get("plugin", "version")
            if not version:
                plugin_ini = os.path.join(path, "plugin.ini")
                if os.path.exists(plugin_ini):
                    cp = ConfigParser()
                    with open(plugin_ini, "r", encoding="UTF-8") as f:
                        cp.read_file(f)
                    version = cp.get("plugin", "version")
            if not version:
                return None

        expansion = Expansion(path, arch_path, version=version)
        expansion.load_provides()
        return expansion

    def find_resource(self, name):
        plugin = self._provides[name]
        return PluginResource(plugin, name)

    def find_executable_development(self, name):
        if System.windows:
            exe_name = name + ".exe"
        else:
            exe_name = name
        if name == "x64sc-fs":
            logger.debug("Lookup hack for vice-fs/x64sc-fs")
            name = "vice-fs"
        # if os.path.basename(os.getcwd()) == "fs-uae-launcher-private":
        #     if name == "fs-uae":
        #         name = "fs-uae-private"
        if os.path.basename(os.getcwd()).endswith("-private"):
            dir_name = name + "-private"
        else:
            dir_name = name

        # See if we can find the executable in a project dir side by side
        path = os.path.join(fsboot.executable_dir(), "..", dir_name, exe_name)
        logger.debug("Checking %s", path)
        # Try one additional level up
        # if not os.path.exists(path):
        #     path = os.path.join(
        #         fsboot.executable_dir(), "..", "..", name, exe_name
        #     )
        #     logger.debug("Checking %s", path)
        if os.path.exists(path):
            logger.debug("Found non-plugin executable %s", path)
            # We want to be able to load bundled libraries from the
            # development directory, before the emulator has been
            # standalone-ified.
            return Executable(path, ld_library_path=True)
        return None

    def find_executable(self, name):
        logger.debug("PluginManager.find_executable %s", repr(name))
        if fsboot.development():
            executable = self.find_executable_development(name)
            if executable:
                return executable
        try:
            plugin = self.provides()["executable:" + name]
        except KeyError:
            # Did not find executable in plugin, try to find executable
            # bundled with the program.
            if System.windows:
                exe_name = name + ".exe"
            else:
                exe_name = name
            path = os.path.join(fsboot.executable_dir(), exe_name)
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
            if System.windows:
                module_name = name + ".dll"
            else:
                module_name = name + ".so"
            path = os.path.join(fsboot.executable_dir(), module_name)
            if os.path.exists(path):
                logger.debug("Found non-plugin module %s", path)
                return path
            return None
        return plugin.library_path(name)

    def find_file_by_sha1(self, sha1):
        try:
            plugin = self.provides()["sha1:" + sha1]
        except KeyError:
            path = None
        else:
            path = plugin.sha1_path(sha1)
        logger.debug("PluginManager.find_file_by_sha1 %s -> %s", sha1, path)
        return path
