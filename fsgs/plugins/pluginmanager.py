import os
import platform
import traceback
from configparser import ConfigParser, NoSectionError
from operator import itemgetter, attrgetter, methodcaller
from fsbc.system import windows, linux, macosx
from fsgs.FSGSDirectories import FSGSDirectories

class Plugin:

    def __init__(self, name, version, path, cp):
        self.name = name
        self.version = version
        self.path = path
        self.provides = {}
        self.load_provides(cp)

    def load_provides(self, cp):
        print("loading provides for", self.path, self.platform())
        try:
            for key, value in cp.items(self.platform()):
                self.provides[key] = value
        except NoSectionError:
            pass

    @staticmethod
    def platform():
        if windows:
            os_name = "windows"
        elif macosx:
            os_name = "macosx"
        elif linux:
            if os.environ.get("STEAM_RUNTIME", ""):
                os_name = "steamos"
            else:
                os_name = "linux"
        else:
            raise Exception("unknown plugin os")
        if platform.machine().lower() in ["x86_64", "x86-64", "amd64", "i386", "i486", "i586", "i686"]:
            if platform.architecture()[0] == "64bit":
                arch = "x86-64"
            else:
                arch = "x86"
        else:
            raise Exception("unknown plugin arch")
        return os_name + "_" + arch


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


class PluginManager:

    __instance = None

    def __init__(self):
        self.provides = {}
        self.plugins = []
        self.load_plugins()
        for plugin in self.plugins:
            for key, value in plugin.provides.items():
                self.provides[key] = plugin

    def load_plugins(self):
        plugins_dir = FSGSDirectories.get_plugins_dir()
        for name in os.listdir(plugins_dir):
            plugin_dir = os.path.join(plugins_dir, name)
            try:
                plugin = self.load_plugin(plugin_dir)
            except Exception:
                traceback.print_exc()
                continue
            if plugin is None:
                continue
            self.plugins.append(plugin)
        self.plugins.sort(key=attrgetter("name"))

    def load_plugin(self, plugin_dir):
        plugin_ini = os.path.join(plugin_dir, "plugin.ini")
        name = os.path.basename(plugin_dir).split("_")[0]
        if not os.path.exists(plugin_ini):
            return None
        cp = ConfigParser()
        with open(plugin_ini, "r", encoding="UTF-8") as f:
            cp.read_file(f)
        version = cp.get("plugin", "version")
        plugin = Plugin(name, version, os.path.join(plugin_dir, version), cp)
        return plugin

    @classmethod
    def instance(cls):
        if cls.__instance is None:
            cls.__instance = cls()
        return cls.__instance

    def find_resource(self, name):
        plugin = self.provides[name]
        return PluginResource(plugin, name)

    def find_executable(self, name):
        print("PluginManager.find_executable", name)
        if windows:
            name = "{0}.exe".format(name)
        elif macosx:
            name = "{0}.app/Contents/MacOS/{0}".format(name)

        for plugin in self.plugins:
            path = os.path.join(plugin.path, Plugin.platform(), name)
            print("check", path)
            if os.path.exists(path):
                return PluginExecutable(plugin, path)
