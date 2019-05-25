from launcher.settings.scan_paths_group import ScanPathsGroup

import fsui
from fsgs.option import Option
from launcher.i18n import gettext
from launcher.settings.settings_page import SettingsPage


class ScanSettingsPage(SettingsPage):
    def __init__(self, parent):
        super().__init__(parent)
        icon = fsui.Icon("indexing-settings", "pkg:workspace")
        gettext("File Database Settings")
        title = gettext("File Database")
        subtitle = gettext(
            "Choose what folders you want to scan for Amiga " "files"
        )
        self.add_header(icon, title, subtitle)

        self.layout.add(
            fsui.MultiLineLabel(
                self,
                gettext(
                    "Choose what folders you want to scan for Amiga " "files"
                ),
            ),
            fill=True,
            margin_bottom=10,
        )
        self.scan_paths_group = ScanPathsGroup(self)
        self.layout.add(self.scan_paths_group, fill=True, expand=True)

        # For reset to defaults function
        self.options_on_page.add(Option.SEARCH_PATH)
