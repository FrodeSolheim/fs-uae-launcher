import logging
import os
import platform
import subprocess
import traceback
from configparser import ConfigParser, NoSectionError
from operator import attrgetter
from fsbc.system import windows, linux, macosx
from fsgs.FSGSDirectories import FSGSDirectories

logger = logging.getLogger("PLUGINS")


class BasePlugin:

    def __init__(self, path, name):
        self.path = path
        self.name = name
        self._provides = {}

    def add_provide(self, key, value):
        self._provides[key] = value

    def provides(self):
        return self._provides


class Plugin(BasePlugin):

    def __init__(self, path, name, version, cp):
        super().__init__(path, name)
        self.version = version
        self.load_provides(cp)

    def load_provides(self, cp):
        logger.debug("loading provides for %s %s", self.path, self.platform())
        try:
            for key, value in cp.items(self.platform()):
                self.provides[key] = value
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
        elif macosx:
            if pretty:
                return "OSX"
            return "macosx"
        elif linux:
            if os.environ.get("STEAM_RUNTIME", ""):
                if pretty:
                    return "SteamOS"
                return "steamos"
            else:
                if pretty:
                    return "Linux"
                return "linux"
        else:
            if pretty:
                return "Unknown"
            return "unknown"

    @staticmethod
    def arch_name(pretty=False):
        if platform.machine().lower() in ["x86_64", "x86-64", "amd64",
                                          "i386", "i486", "i586", "i686"]:
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
        super().__init__(path, name)
        self._arch_path = arch_path

    def load_provides(self):
        logger.debug("Loading provides for %s", repr(self.path))
        for item in os.listdir(self._arch_path):
            path = os.path.join(self._arch_path, item)
            if windows:
                if item.endswith(".exe"):
                    self.add_provide("executable:" + item[:-4].lower(), path)
            else:
                if path.endswith(".so"):
                    self.add_provide("library:" + item.lower()[:-3], path)
                elif os.access(path, os.X_OK):
                    self.add_provide("executable:" + item.lower(), path)
            if macosx:
                if path.endswith(".app"):
                    app_path = os.path.join(
                        path, "Contents", "MacOS")
                    if os.path.exists(app_path):
                        for app_item in os.listdir(app_path):
                            p = os.path.join(app_path, app_item)
                            if os.access(p, os.X_OK):
                                self.add_provide(
                                    "executable:" + app_item.lower(), p)

    def executable(self, name):
        path = self.provides()["executable:" + name]
        return PluginExecutable(self, path)

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


class PluginExecutable:

    def __init__(self, plugin, path):
        self.plugin = plugin
        self.path = path

    def popen(self, args, env=None, **kwargs):
        # logger.debug("PluginExecutable.popen %s %s %s",
        #              repr(args), repr(env), repr(kwargs))
        args = [self.path] + args
        if env:
            env = env.copy()
        else:
            env = os.environ.copy()
        if windows:
            pass
        elif macosx:
            pass
        else:
            env["LD_LIBRARY_PATH"] = os.path.dirname(self.path)
        return subprocess.Popen(args, env=env, **kwargs)


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
                FSGSDirectories.get_base_dir(), "Workspace", "Expansion")
        if expansion_dir and os.path.isdir(expansion_dir):
            result.append(expansion_dir)
        return result

    def __init__(self):
        self._provides = {}
        self._plugins = []
        self.load_plugins()
        for plugin in self._plugins:
            for key, value in plugin.provides().items():
                self._provides[key] = plugin

    def plugins(self):
        return self._plugins.copy()

    def provides(self):
        return self._provides.copy()

    def load_plugins(self):
        for dir_path in self.plugin_path():
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
            self._plugins.sort(key=attrgetter("name"))

    def load_plugin(self, plugin_dir):
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
        arch_path = os.path.join(path, Plugin.os_name(pretty=True),
                                 Plugin.arch_name(pretty=True))
        version_path = os.path.join(arch_path, "Version.txt")
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
            return None
        return plugin.executable(name)

        # if windows:
        #     name = "{0}.exe".format(name)
        # elif macosx:
        #     name = "{0}.app/Contents/MacOS/{0}".format(name)

        # for plugin in self._plugins:
        #     path = os.path.join(plugin.path, Plugin.platform(), name)
        #     print("check", path)
        #     if os.path.exists(path):
        #         return PluginExecutable(plugin, path)
