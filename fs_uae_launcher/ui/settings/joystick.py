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


class JoystickSettingsPage(fsui.Panel):

    def __init__(self, parent):
        fsui.Panel.__init__(self, parent)
        self.layout = fsui.VerticalLayout()
        # self.layout.set_padding(20, 20, 20, 20)

        self.icon_header = IconHeader(
            self, fsui.Icon("joystick-settings", "pkg:fs_uae_workspace"),
            gettext("Joystick Settings"),
            gettext("Configure joysticks and set preferred joystick devices"))
        self.layout.add(self.icon_header, fill=True, margin_bottom=20)

        self.list_view = fsui.ListView(self)
        self.list_view.set_min_height(140)
        self.list_view.item_activated.connect(self.on_joystick_activated)
        image = fsui.Image("fs_uae_workspace:res/16/gamepad.png")
        for device_name in DeviceManager.get_joystick_names():
            if DeviceManager.is_joystick(device_name):
                self.list_view.add_item(device_name, icon=image)
        self.layout.add(self.list_view, fill=True, expand=True)

        label = fsui.Label(
            self, gettext("Double-click a device entry to configure it (map "
                          "joystick buttons)."))
        self.layout.add(label, margin_top=10)

        self.layout.add_spacer(20)
        self.pref_group = PreferredJoysticksGroup(self)
        self.layout.add(self.pref_group, fill=True)

    def on_joystick_activated(self, index):
        device_name = self.list_view.get_item(index)
        print(self.get_window())
        shell_open("Workspace:Tools/JoystickConfig", [device_name],
                   parent=self.get_window())
