from launcher.settings.maintenance_settings_page import DefragmentDatabasesTask

import fsboot
import fsui
from fsui.extra.taskdialog import TaskDialog
from launcher.option import Option
from launcher.res import gettext
from launcher.settings.settings_page import SettingsPage


class LauncherSettingsPage(SettingsPage):
    def __init__(self, parent):
        super().__init__(parent)
        icon = fsui.Icon("fs-uae-launcher", "pkg:launcher")
        self.add_header(icon, "FS-UAE Launcher")

        if fsboot.get("fws") == "1":
            # We omit the appearance settings, since they have no effect
            # when running under the workspace environment.
            pass
        else:
            self.add_option(Option.LAUNCHER_THEME)
            self.add_option(Option.LAUNCHER_FONT_SIZE)

        self.add_option(Option.LAUNCHER_CLOSE_BUTTONS)

        self.add_section(gettext("Experimental Features"))
        # Netplay feature is now enabled by default
        # self.add_option(Option.NETPLAY_FEATURE)
        self.add_option(Option.PLATFORMS_FEATURE)
        # self.add_option(Option.LAUNCHER_CONFIG_FEATURE)
        # self.add_option(Option.LAUNCHER_SETUP_WIZARD_FEATURE)

        self.add_section(gettext("Maintenance"))
        label = fsui.MultiLineLabel(self, gettext(
            "Defragmenting the databases will improve performance "
            "by ensuring that tables and indices are stored contiguously "
            "on disk. It will also reclaim some storage space."), 640)
        self.layout.add(label, fill=True, margin_top=20)
        button = fsui.Button(self, gettext("Defragment Databases"))
        button.activated.connect(self.on_defragment_button)
        self.layout.add(button, margin_top=20)

    def on_defragment_button(self):
        TaskDialog(self.get_window(), DefragmentDatabasesTask()).show()
