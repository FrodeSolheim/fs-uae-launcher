import fsui
from fs_uae_workspace.shell import SimpleApplication
from fs_uae_launcher.ui.settings.AudioSettingsPage import AudioSettingsPage
from fs_uae_launcher.res import gettext


class SettingsWindow(fsui.Window):

    def __init__(self):
        fsui.Window.__init__(self, None, gettext("Audio Settings"))
        self.layout = fsui.VerticalLayout()
        page = AudioSettingsPage(self)
        page.set_min_width(700)
        self.layout.add(page, fill=True)
        self.set_size(self.layout.get_min_size())

    def __del__(self):
        print("SettingsWindow.__del__")


application = SimpleApplication(SettingsWindow)
