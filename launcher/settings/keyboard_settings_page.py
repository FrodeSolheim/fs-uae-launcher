import fsui
from launcher.i18n import gettext
from launcher.settings.settings_page import SettingsPage


class KeyboardSettingsPage(SettingsPage):
    def __init__(self, parent):
        super().__init__(parent)
        icon = fsui.Icon("keyboard-settings", "pkg:workspace")
        gettext("Keyboard Settings")
        title = gettext("Keyboard")
        subtitle = ""
        self.add_header(icon, title, subtitle)

        self.add_option("keyboard_input_grab")
        self.add_option("full_keyboard")
        self.add_option("swap_ctrl_keys")
        self.add_option("raw_input")

        self.add_section(gettext("Key Mapping"))

        self.add_option("keyboard_key_backslash")
        self.add_option("keyboard_key_equals")
        self.add_option("keyboard_key_insert")
        self.add_option("keyboard_key_less")
