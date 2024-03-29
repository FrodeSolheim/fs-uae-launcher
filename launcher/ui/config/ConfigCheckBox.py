import fsui
from launcher.context import get_config


class ConfigCheckBox(fsui.CheckBox):
    def __init__(self, parent, label, config_key):
        fsui.CheckBox.__init__(self, parent, label)
        self.config_key = config_key
        self.initialize_from_config()
        self.set_config_handlers()

    def initialize_from_config(self):
        self.on_config(self.config_key, get_config(self).get(self.config_key))

    def set_config_handlers(self):
        get_config(self).add_listener(self)

    def onDestroy(self):
        get_config(self).remove_listener(self)
        super().onDestroy()

    def on_changed(self):
        if self.checked():
            get_config(self).set(self.config_key, "1")
        else:
            get_config(self).set(self.config_key, "")

    def on_config(self, key: str, value: str):
        if key == self.config_key:
            self.setChecked(value == "1")
