import fsui
from fswidgets.widget import Widget
from launcher.i18n import gettext
from launcher.settings.settings_page import SettingsPage
from system.prefs.components.notworking import PrefsNotWorkingWarningPanel


class MouseSettingsPage(SettingsPage):
    def __init__(self, parent: Widget) -> None:
        super().__init__(parent)

        PrefsNotWorkingWarningPanel(parent=self)
        self.layout.add_spacer(20)

        icon = fsui.Icon("mouse-settings", "pkg:workspace")
        gettext("Mouse Settings")
        title = gettext("Mouse")
        subtitle = ""
        self.add_header(icon, title, subtitle)

        self.add_option("automatic_input_grab")
        self.add_option("initial_input_grab")
        self.add_option("middle_click_ungrab")
        self.add_option("mouse_speed")
        self.add_option("joystick_port_0_autoswitch")
