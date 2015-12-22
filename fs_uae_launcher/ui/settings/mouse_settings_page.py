import fsui
from fs_uae_launcher.I18N import gettext
from fs_uae_launcher.ui.settings.settings_page import SettingsPage


class MouseSettingsPage(SettingsPage):

    def __init__(self, parent):
        super().__init__(parent)
        icon = fsui.Icon("mouse-settings", "pkg:fs_uae_workspace")
        gettext("Mouse Settings")
        title = gettext("Mouse")
        subtitle = ""
        self.add_header(icon, title, subtitle)

        self.add_option("automatic_input_grab")
        self.add_option("initial_input_grab")
        self.add_option("middle_click_ungrab")
        self.add_option("mouse_speed")
