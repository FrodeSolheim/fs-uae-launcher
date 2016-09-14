import sys
from fsgs.plugins.plugin_manager import PluginManager
"""
Mednafen-FS launcher script used for testing.
"""


def app_main():
    executable = PluginManager.instance().find_executable("mednafen-fs")
    process = executable.popen(sys.argv[1:])
    process.wait()
