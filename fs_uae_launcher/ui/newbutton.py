from fs_uae_launcher.Config import Config
from fs_uae_launcher.I18N import gettext
from fs_uae_launcher.Settings import Settings
from fs_uae_launcher.ui.IconButton import IconButton


class NewButton(IconButton):

    def __init__(self, parent):
        super().__init__(parent, "new_button.png")
        self.set_tooltip(gettext("New Configuration"))

    def on_activate(self):
        self.new_config()

    @staticmethod
    def new_config():
        Config.load_default_config()
        # Settings.set("config_changed", "1")
        Settings.set("parent_uuid", "")
