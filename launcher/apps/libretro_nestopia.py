import sys
from fsgs.plugins.pluginmanager import PluginManager

"""
RetroArch launcher script used for testing.
"""


# FIXME: Use from RetroArchDriver
def find_libretro_core(name):
    return "/usr/lib/x86_64-linux-gnu/libretro/{}.so".format(name)


def app_main():
    executable = PluginManager.instance().find_executable("retroarch")

    args = sys.argv[1:]
    libretro_core = find_libretro_core("nestopia_libretro")
    args.extend(["-L", libretro_core])

    process = executable.popen(args)
    process.wait()
