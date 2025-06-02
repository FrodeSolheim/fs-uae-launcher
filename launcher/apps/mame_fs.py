import sys

from fsgs.plugins.pluginmanager import PluginManager

"""
MAME-FS launcher script used for testing.
"""


def app_main():
    executable = PluginManager.instance().find_executable("mame-fs")
    process = executable.popen(sys.argv[1:])
    process.wait()
