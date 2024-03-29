import fsui
from fsgamesys.options.option import Option
from fswidgets.widget import Widget
from launcher.i18n import t
from launcher.settings.scan_paths_group import ScanPathsGroup
from launcher.settings.settings_page import SettingsPage


class ScanSettingsPage(SettingsPage):
    def __init__(self, parent: Widget):
        super().__init__(parent)
        # icon = fsui.Icon("indexing-settings", "pkg:workspace")
        # t("File Database Settings")
        # title = t("File Database")
        description = t(
            "Choose what folders you want to scan for media files and ROMs"
        )
        # self.add_header(icon, title, description)

        self.layout.add(
            fsui.MultiLineLabel(self, description),
            fill=True,
            margin_bottom=10,
        )
        self.scan_paths_group = ScanPathsGroup(self)
        self.layout.add(self.scan_paths_group, fill=True, expand=True)

        # For reset to defaults function
        self.options_on_page.add(Option.SEARCH_PATH)
