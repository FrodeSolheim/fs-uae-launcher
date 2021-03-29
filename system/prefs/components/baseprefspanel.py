from fsui import HeadingLabel, Panel
from launcher.settings.option_ui import OptionUI


class BasePrefsPanel(Panel):
    def __init__(self, parent):
        super().__init__(parent)

        self.optionsOnPanel = set()
        # self.options_on_page = set()

    # def add_header(self, icon, title, subtitle=""):
    #     self.icon_header = SettingsHeader(self, icon, title, subtitle)
    #     self.layout.add(self.icon_header, fill=True, margin_bottom=20)

    def add_option(self, name, description="", margin_top=10, warnings=None):
        group = OptionUI.create_group(
            self, name, description=description, warnings=warnings
        )
        self.layout.add(
            group, fill=True, margin_top=margin_top, margin_bottom=10
        )
        # self.options_on_page.add(name)
        return group

    def add_section(self, title, margin_top=20, margin_bottom=20):
        label = HeadingLabel(self, title)
        self.layout.add(
            label, margin_top=margin_top, margin_bottom=margin_bottom
        )

    # def reset_to_defaults(self):
    #     for option in self.options_on_page:
    #         LauncherSettings.set(option, "")
