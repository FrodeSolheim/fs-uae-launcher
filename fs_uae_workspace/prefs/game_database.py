from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import fsui
from fs_uae_workspace.shell import SimpleApplication
from fs_uae_launcher.ui.settings.GameDatabaseSettingsPage import \
    GameDatabaseSettingsPage
from fs_uae_launcher.res import gettext


class SettingsWindow(fsui.Window):

    def __init__(self):
        fsui.Window.__init__(self, None, gettext("Game Database Settings"))
        self.layout = fsui.VerticalLayout()
        page = GameDatabaseSettingsPage(self)
        page.set_min_width(700)
        self.layout.add(page, fill=True)
        self.set_size(self.layout.get_min_size())

    def __del__(self):
        print("SettingsWindow.__del__")


application = SimpleApplication(SettingsWindow)
