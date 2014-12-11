from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import fsui as fsui
from fsui.extra.iconheader import IconHeader
from ...I18N import gettext
from .PreferredJoysticksGroup import PreferredJoysticksGroup
from fs_uae_workspace.shell import shell_open
from fs_uae_launcher.DeviceManager import DeviceManager
from .CustomSettingsPage import CustomSettingsPage


class AdvancedSettingsPage(fsui.Panel):

    def __init__(self, parent):
        fsui.Panel.__init__(self, parent)
        self.layout = fsui.VerticalLayout()
        # self.layout.set_padding(20, 20, 20, 20)

        self.icon_header = IconHeader(
            self, fsui.Icon("settings", "pkg:fs_uae_workspace"),
            gettext("Advanced Settings"),
            gettext("Specify global options and settings which does "
                    "not have UI controls"))
        self.layout.add(self.icon_header, fill=True, margin_bottom=20)
        self.layout.add(CustomSettingsPage(self), fill=True, expand=True)
