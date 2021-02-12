import os

from fsgamesys.FSGSDirectories import FSGSDirectories


class PluginHelper(object):
    def __init__(self):
        pass

    def find_resource_dirs(self, resource_name):
        resource_dirs = []
        for plugin in self.find_plugins_with_resource(resource_name):
            resource_dir = os.path.join(plugin, resource_name)
            resource_dirs.append(resource_dir)
        return resource_dirs

    @staticmethod
    def find_plugins():
        plugins = []
        plugins_dir = FSGSDirectories.get_plugins_dir()
        if plugins_dir is None:
            return plugins
        for item in os.listdir(plugins_dir):
            plugin_dir = os.path.join(plugins_dir, item)
            if not os.path.isdir(plugin_dir):
                continue
            if os.path.exists(os.path.join(plugin_dir, "disabled")):
                continue
            plugins.append(plugin_dir)
        return plugins

    def find_plugins_with_resource(self, resource_name):
        plugins = []
        for plugin_dir in self.find_plugins():
            resource_dir = os.path.join(plugin_dir, resource_name)
            if os.path.exists(resource_dir):
                plugins.append(plugin_dir)
        return plugins
