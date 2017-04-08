import fsui
from launcher.launcher_settings import LauncherSettings
from launcher.settings.option_ui import OptionUI
from launcher.settings.settings_header import SettingsHeader


class SettingsPage(fsui.Panel):

    def __init__(self, parent):
        super().__init__(parent)
        self.layout = fsui.VerticalLayout()
        self.layout.padding_top = 20
        self.layout.padding_bottom = 20
        self.layout.padding_left = 20
        self.layout.padding_right = 20
        self.icon_header = None
        self.options_on_page = set()

    def add_header(self, icon, title, subtitle=""):
        self.icon_header = SettingsHeader(self, icon, title, subtitle)
        self.layout.add(self.icon_header, fill=True, margin_bottom=20)

    def add_option(self, name, description=""):
        group = OptionUI.create_group(self, name, description=description)
        self.layout.add(group, fill=True, margin_top=10, margin_bottom=10)
        self.options_on_page.add(name)
        return group

    def add_section(self, title):
        label = fsui.HeadingLabel(self, title)
        self.layout.add(label, margin_top=20, margin_bottom=20)

    def reset_to_defaults(self):
        for option in self.options_on_page:
            LauncherSettings.set(option, "")
