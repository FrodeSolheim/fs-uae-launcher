import fsui
from fsgamesys.plugins.pluginmanager import PluginManager
from launcher.res import gettext
from launcher.settings.settings_page import SettingsPage


class PluginsSettingsPage(SettingsPage):
    def __init__(self, parent):
        super().__init__(parent)
        icon = fsui.Icon("plugins", "pkg:workspace")
        self.add_header(icon, gettext("Plugins"))

        self.list_view = fsui.ListView(self)
        self.list_view.set_min_height(140)
        # self.list_view.item_activated.connect(self.on_plugin_activated)
        image = fsui.Image("workspace:/data/16x16/settings.png")
        plugin_manager = PluginManager.instance()
        for plugin in plugin_manager.plugins():
            text = "{0} ({1})".format(plugin.name, plugin.version)
            if plugin.outdated:
                text += " - " + gettext("This plugin is outdated").upper()
            print("[PLUGINS] {0}".format(text))
            self.list_view.add_item(text, icon=image)
        self.layout.add(self.list_view, fill=True, expand=True)
