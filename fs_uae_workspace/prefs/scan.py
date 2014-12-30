import fsui
from fs_uae_workspace.shell import SimpleApplication
from fs_uae_launcher.ui.settings.ScanSettingsPage import ScanSettingsPage
from fs_uae_launcher.res import gettext


class SettingsWindow(fsui.Window):

    def __init__(self):
        fsui.Window.__init__(self, None, gettext("Scan Settings"))
        self.layout = fsui.VerticalLayout()
        page = ScanSettingsPage(self)
        page.set_min_width(700)
        self.layout.add(page, fill=True)
        self.set_size(self.layout.get_min_size())

    def __del__(self):
        print("SettingsWindow.__del__")


application = SimpleApplication(SettingsWindow)
