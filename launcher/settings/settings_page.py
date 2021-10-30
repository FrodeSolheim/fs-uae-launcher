from typing import Set

import fsui
from fsui.qt.icon import Icon
from fswidgets.widget import Widget
from launcher.fswidgets2.style import Style
from launcher.launcher_settings import LauncherSettings
from launcher.settings.option_ui import OptionUI
from launcher.settings.settings_header import SettingsHeader


class SettingsPage(fsui.Panel):
    def __init__(self, parent: Widget):
        super().__init__(parent)
        self.layout = fsui.VerticalLayout()
        self.layout.padding_top = 20
        self.layout.padding_bottom = 20
        self.layout.padding_left = 20
        self.layout.padding_right = 20
        self.icon_header = None
        self.options_on_page: Set[str] = set()
        self.style = Style({"flexGrow": 1})

    def create_option_label(self, parent, label):
        return OptionUI.create_option_label(parent, label)

    def add_header(self, icon: Icon, title: str, subtitle: str = ""):
        self.icon_header = SettingsHeader(self, icon, title, subtitle)
        self.layout.add(self.icon_header, fill=True, margin_bottom=20)

    def add_divider(self):  # , top_margin=10, bottom_margin=10):
        OptionUI.add_divider(
            self,
            self.layout,
            # top_margin=top_margin,
            # bottom_margin=bottom_margin,
        )
        # # return
        # panel = fsui.Panel(self)
        # panel.set_background_color(fsui.Color(0xA2A2A2))
        # panel.set_min_height(1)
        # self.layout.add(
        #     panel,
        #     fill=True,
        #     margin_top=top_margin,
        #     margin_bottom=bottom_margin,
        # )

    def add_option(
        self,
        name: str,
        description: str = "",
        margin_top: int = 10,
        margin_bottom: int = 10,
        warnings=None,
    ):
        group = OptionUI.create_group(
            self, name, description=description, warnings=warnings
        )
        self.layout.add(
            group,
            fill=True,
            margin_top=margin_top,
            margin_bottom=margin_bottom,
        )
        self.options_on_page.add(name)
        return group

    def add_section(self, title):
        label = fsui.HeadingLabel(self, title)
        self.layout.add(label, margin_top=20, margin_bottom=20)

    def reset_to_defaults(self):
        for option in self.options_on_page:
            LauncherSettings.set(option, "")
