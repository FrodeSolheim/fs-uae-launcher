import fsui
from fs_uae_launcher.ui.settings.option_ui import OptionUI
from fs_uae_launcher.ui.settings.settings_header import SettingsHeader


class SettingsPage(fsui.Panel):

    def __init__(self, parent):
        super().__init__(parent)
        self.layout = fsui.VerticalLayout()
        self.icon_header = None

    def add_header(self, icon, title, subtitle=""):
        self.icon_header = SettingsHeader(self, icon, title, subtitle)
        self.layout.add(self.icon_header, fill=True, margin_bottom=20)

    def add_option(self, name):
        group = OptionUI.create_group(self, name)
        self.layout.add(group, fill=True, margin_top=10, margin_bottom=10)
        return group

    def add_section(self, title):
        label = fsui.HeadingLabel(self, title)
        self.layout.add(label, margin_top=20, margin_bottom=20)
