import os
import sys
import platform
import functools

from fsgs.plugins.pluginmanager import PluginManager


@functools.lru_cache()
def find(name):
    return Expansion(name)


@functools.lru_cache()
def cpu_name():
    machine = platform.machine().lower()
    if machine in ["x86_64", "amd64", "i386", "i486", "i585", "i686"]:
        if platform.architecture()[0] == "32bit":
            return "x86"
        if platform.architecture()[0] == "64bit":
            return "x86-64"
    if machine.startswith("power"):
        if platform.architecture()[0] == "32bit":
            return "PPC"
    raise Exception("Unknown CPU")


@functools.lru_cache()
def os_name():
    if sys.platform.startswith("linux"):
        return "Linux"
    if sys.platform == "win32":
        return "Windows"
    if sys.platform == "darwin":
        return "OSX"
    raise Exception("Unknown OS")


class Expansion:
    def __init__(self, name):
        self.path = os.path.join("Workspace", "Expansion", name)
        assert os.path.isdir(self.path)

    @classmethod
    def find(cls, name):
        return find(name)

    @functools.lru_cache()
    def executable(self, name):
        path = self.path
        path = os.path.join(path, os_name(), cpu_name())
        path = os.path.join(path, name)
        if os_name() == "Windows":
            path += ".exe"
        return path


def find_executable(name):
    return PluginManager.instance().find_executable(name)
