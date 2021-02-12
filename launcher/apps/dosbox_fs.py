import sys

from fsgamesys.plugins.pluginmanager import PluginManager

"""
DOSBox-FS launcher script used for testing.
"""


def app_main():
    executable = PluginManager.instance().find_executable("dosbox-fs")
    process = executable.popen(sys.argv[1:])
    process.wait()
