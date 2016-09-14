from fsgs.plugins.plugin_manager import PluginManager
"""
Debug script used to dump information about detected plugins
"""


def app_main():
    plugin_manager = PluginManager.instance()
    plugins = plugin_manager.plugins()
    provides = plugin_manager.provides()

    print("")
    print("Plugins:")
    for plugin in plugins:
        print("* {} ({})".format(plugin.name, type(plugin).__name__))
        print(" ", plugin.path)

    print("")
    print("Provides:")
    for name in sorted(provides):
        plugin = provides[name]
        print("* {} ({})".format(name, plugin.name))
        # print("", plugin.provides()[name])

    print("")
