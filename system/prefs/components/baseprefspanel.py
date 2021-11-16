from typing import Set

from fsui import HeadingLabel, Panel
from fswidgets.widget import Widget
from launcher.settings.option_ui import OptionUI


class BasePrefsPanel(Panel):
    def __init__(self, parent: Widget):
        super().__init__(parent)

        # self.set_min_size((520, 0))

        self.optionsOnPanel: Set[str] = set()
        # self.options_on_page = set()

    # def add_header(self, icon, title, subtitle=""):
    #     self.icon_header = SettingsHeader(self, icon, title, subtitle)
    #     self.layout.add(self.icon_header, fill=True, margin_bottom=20)

    def add_option(
        self,
        name: str,
        description: str = "",
        margin_top: int = 10,
        warnings=None,
    ) -> Panel:
        group = OptionUI.create_group(
            self, name, description=description, warnings=warnings
        )
        self.layout.add(
            group, fill=True, margin_top=margin_top, margin_bottom=10
        )
        # self.options_on_page.add(name)
        return group

    def add_section(
        self, title: str, margin_top: int = 20, margin_bottom: int = 20
    ):
        label = HeadingLabel(self, title)
        self.layout.add(
            label, margin_top=margin_top, margin_bottom=margin_bottom
        )

    # def reset_to_defaults(self):
    #     for option in self.options_on_page:
    #         LauncherSettings.set(option, "")
