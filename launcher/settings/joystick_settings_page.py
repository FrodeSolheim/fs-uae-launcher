import fsui
from fsgs.option import Option
from launcher.devicemanager import DeviceManager
from launcher.i18n import gettext
from launcher.launcher_settings import LauncherSettings
from launcher.settings.settings_page import SettingsPage
from workspace.apps.joystick_config_app import JoystickConfigWindow


class JoystickSettingsPage(SettingsPage):
    def __init__(self, parent):
        super().__init__(parent)
        icon = fsui.Icon("joystick-settings", "pkg:workspace")
        # gettext("Joystick Settings")
        title = gettext("Controllers")
        subtitle = gettext(
            "Configure joysticks and set preferred joystick devices"
        )
        self.add_header(icon, title, subtitle)

        label = fsui.Label(
            self, gettext("Double-click a controller to configure it:")
        )
        self.layout.add(label, margin_bottom=10)

        self.list_view = fsui.ListView(self)
        self.list_view.set_min_height(140)
        self.list_view.item_activated.connect(self.on_joystick_activated)
        image = fsui.Image("workspace:res/16x16/gamepad.png")
        for device_name in DeviceManager.get_joystick_names():
            if DeviceManager.is_joystick(device_name):
                self.list_view.add_item(device_name, icon=image)
        self.layout.add(self.list_view, fill=True, expand=True)

        self.layout.add_spacer(20)
        self.pref_group = PreferredJoysticksGroup(self)
        self.layout.add(self.pref_group, fill=True)

        # For reset to defaults function
        self.options_on_page.add(Option.PRIMARY_JOYSTICK)
        self.options_on_page.add(Option.SECONDARY_JOYSTICK)

    def on_joystick_activated(self, index):
        device_name = self.list_view.get_item(index)
        print(self.get_window())
        # shell_open("Workspace:Tools/JoystickConfig", [device_name],
        #            parent=self.get_window())
        JoystickConfigWindow(self.window, device_name).show()


joystick_mode_values = ["nothing", "mouse", "joystick"]
joystick_values = ["none", "mouse", "keyboard"]


class PreferredJoysticksGroup(fsui.Group):
    def __init__(self, parent):
        fsui.Group.__init__(self, parent)
        self.layout = fsui.HorizontalLayout()
        # self.layout.padding_left = 10
        # self.layout.padding_right = 10

        # image = fsui.Image("launcher:res/joystick.png")
        # self.image_view = fsui.ImageView(self, image)
        # self.layout.add(self.image_view, valign=0.0)

        # self.layout.add_spacer(20)

        self.layout2 = fsui.VerticalLayout()
        self.layout.add(self.layout2, fill=True, expand=True)

        heading = gettext("Preferred Controllers")
        label = fsui.HeadingLabel(self, heading)
        self.layout2.add(label)

        self.layout2.add_spacer(20)
        label = fsui.Label(self, gettext("Preferred controller (if present):"))
        self.layout2.add(label)

        self.layout2.add_spacer(6)
        selector = PreferredJoystickSelector(self, 0)
        self.layout2.add(selector, fill=True)

        self.layout2.add_spacer(20)
        label = fsui.Label(
            self, gettext("Preferred device for secondary controller:")
        )
        self.layout2.add(label)

        self.layout2.add_spacer(6)
        selector = PreferredJoystickSelector(self, 1)
        self.layout2.add(selector, fill=True)


class PreferredJoystickSelector(fsui.Group):
    def __init__(self, parent, index):
        self.index = index
        if index:
            self.key = Option.SECONDARY_JOYSTICK
        else:
            self.key = Option.PRIMARY_JOYSTICK

        fsui.Group.__init__(self, parent)
        self.layout = fsui.HorizontalLayout()

        devices = ["", get_keyboard_title()]
        # for i, name in enumerate(DeviceManager.get_joystick_names()):
        #     devices.append(name)
        for device_name in DeviceManager.get_joystick_names():
            if DeviceManager.is_joystick(device_name):
                devices.append(device_name)

        self.device_choice = fsui.ComboBox(self, devices)

        self.layout.add(self.device_choice, expand=True)

        # Config.add_listener(self)

        self.initialize_from_settings()
        self.set_settings_handlers()

    def initialize_from_settings(self):
        self.on_setting(self.key, LauncherSettings.get(self.key))

    def set_settings_handlers(self):
        self.device_choice.on_changed = self.on_device_changed
        LauncherSettings.add_listener(self)

    def on_destroy(self):
        LauncherSettings.remove_listener(self)

    def on_device_changed(self):
        value = self.device_choice.get_text()
        print("on_device_change", value)
        if value == get_keyboard_title():
            value = "keyboard"
        LauncherSettings.set(self.key, value)

    def on_setting(self, key, value):
        if key == self.key:
            if value == "keyboard":
                value = get_keyboard_title()
            self.device_choice.set_text(value)


def get_keyboard_title():
    return gettext("Cursor Keys and Right Ctrl/Alt")
