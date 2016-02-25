import fsui as fsui
from ...launcher_config import LauncherConfig


class ConfigCheckBox(fsui.CheckBox):

    def __init__(self, parent, label, config_key):
        fsui.CheckBox.__init__(self, parent, label)
        self.config_key = config_key
        self.initialize_from_config()
        self.set_config_handlers()

    def initialize_from_config(self):
        self.on_config(self.config_key, LauncherConfig.get(self.config_key))

    def set_config_handlers(self):
        LauncherConfig.add_listener(self)

    def on_destroy(self):
        LauncherConfig.remove_listener(self)

    def on_change(self):
        if self.is_checked():
            LauncherConfig.set(self.config_key, "1")
        else:
            LauncherConfig.set(self.config_key, "")

    def on_config(self, key, value):
        if key == self.config_key:
            if value == "1":
                self.check(True)
            else:
                self.check(False)
