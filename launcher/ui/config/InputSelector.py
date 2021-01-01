import sys

import fsui
from fsgs.platform import Platform
from launcher.context import get_config
from launcher.devicemanager import DeviceManager
from launcher.i18n import gettext
from launcher.launcher_signal import LauncherSignal
from launcher.option import Option
from launcher.ui.HelpButton import HelpButton
from launcher.ui.IconButton import IconButton
from launcher.ui.behaviors.platformbehavior import (
    AMIGA_PLATFORMS,
    AmigaShowBehavior,
)

MIN_TYPE_CHOICE_WIDTH = 200


# FIXME: Superclass was Group, but changed to Panel due to not being able
# to disconnect from listening to config changes when closing window.
class InputSelector(fsui.Panel):
    def __init__(self, parent, port, autofire_button=True):
        self.port = port
        self.device_option_key = "joystick_port_{0}".format(port)
        self.mode_option_key = "joystick_port_{0}_mode".format(port)
        self.autofire_mode_option_key = "joystick_port_{0}_autofire".format(
            port
        )

        super().__init__(parent)
        self.layout = fsui.HorizontalLayout()

        if port == 1:
            non_amiga_port_gui_index = 0
        elif port == 0:
            non_amiga_port_gui_index = 1
        else:
            non_amiga_port_gui_index = port
        self.layout.add(InputPortTypeChoice(self, non_amiga_port_gui_index))

        self.joystick_mode_values = [
            "nothing",
            "joystick",
        ]
        self.joystick_mode_titles = [
            gettext("No Amiga Device"),
            gettext("Amiga Joystick"),
        ]

        if port < 2:
            self.joystick_mode_values.extend(
                ["mouse", "cd32 gamepad",]
            )
            self.joystick_mode_titles.extend(
                [gettext("Amiga Mouse"), gettext("CD32 Pad"),]
            )

        self.mode_choice = fsui.Choice(self, self.joystick_mode_titles)
        self.mode_choice.set_min_width(MIN_TYPE_CHOICE_WIDTH)
        # AmigaEnableBehavior(self.mode_choice)
        AmigaShowBehavior(self.mode_choice)

        self.layout.add(self.mode_choice)
        self.layout.add_spacer(10)
        # else:
        #     self.mode_choice = None
        if port >= 4:
            self.mode_choice.set_enabled(False)

        # devices = ["", _("No Host Device"), _("Mouse"),
        #         _("Cursor Keys and Right Ctrl/Alt")]
        # for i, name in enumerate(DeviceManager.get_joystick_names()):
        #     devices.append(name)
        #     if not self.joystick_values_initialized:
        #         self.joystick_values.append(DeviceManager.device_ids[i])
        # self.joystick_values_initialized = True

        self.device_choice = fsui.ComboBox(self, [""], read_only=True)
        # AmigaEnableBehavior(self.device_choice)
        self.joystick_values = []
        self.rebuild_device_list()
        self.device_choice.set_index(0)
        # print(self.device_choice.index())
        AmigaShowBehavior(self.device_choice)
        self.layout.add(self.device_choice, expand=True)

        self.layout.add(
            InputPortDeviceChoice(self, non_amiga_port_gui_index), expand=True,
        )

        if port < 4 and autofire_button:
            self.autofire_button = IconButton(self, "16x16/lightning_off.png")
            self.autofire_button.activated.connect(self.on_autofire_button)
            self.layout.add(self.autofire_button, margin_left=10)
            AmigaShowBehavior(self.autofire_button)
        else:
            self.autofire_button = None

        if port == 4:
            self.help_button = HelpButton(
                self, "https://fs-uae.net/custom-joystick-port"
            )
            self.layout.add(self.help_button, margin_left=10)

        self.initialize_from_config()
        self.set_config_handlers()

    def rebuild_device_list(self):
        self.joystick_values = ["", "none"]
        devices = ["", gettext("No Host Device")]
        for i, name in enumerate(DeviceManager.get_joystick_names()):
            devices.append(fix_device_name(name))
            self.joystick_values.append(DeviceManager.device_ids[i])
        self.device_choice.set_items(devices)

    def initialize_from_config(self):
        self.on_config(
            self.device_option_key,
            get_config(self).get(self.device_option_key),
        )
        self.on_config(
            self.mode_option_key, get_config(self).get(self.mode_option_key)
        )
        self.on_config(
            self.autofire_mode_option_key,
            get_config(self).get(self.autofire_mode_option_key),
        )

    def set_config_handlers(self):
        if self.mode_choice is not None:
            self.mode_choice.on_changed = self.on_mode_changed
        self.device_choice.on_changed = self.on_device_changed
        get_config(self).add_listener(self)
        LauncherSignal.add_listener("settings_updated", self)
        LauncherSignal.add_listener("device_list_updated", self)

    def on_destroy(self):
        print("InputSelector.on_destroy")
        get_config(self).remove_listener(self)
        LauncherSignal.remove_listener("settings_updated", self)
        LauncherSignal.remove_listener("device_list_updated", self)
        super().on_destroy()

    def on_mode_changed(self):
        if self.mode_choice is not None:
            index = self.mode_choice.index()
            value = self.joystick_mode_values[index]
            self.set_value_or_default(value)

    def set_value_or_default(self, value):
        if self.port == 0:
            if value == "mouse":
                value = ""
        elif self.port == 1:
            if get_config(self).get("amiga_model").startswith("CD32"):
                default = "cd32 gamepad"
            else:
                default = "joystick"
            if value == default:
                value = ""
        else:
            if value == "nothing":
                value = ""
        if get_config(self).get(self.mode_option_key) != value:
            get_config(self).set(self.mode_option_key, value)

    def on_device_changed(self):
        index = self.device_choice.index()

        value = self.joystick_values[index]
        if value != "none":
            # Reset to default device for other ports using the same device.
            for port in range(4):
                if self.port == port:
                    continue
                key = "joystick_port_{0}".format(port)
                if get_config(self).get(key) == value:
                    get_config(self).set(key, "")
        get_config(self).set(self.device_option_key, value)

    def on_autofire_button(self):
        if get_config(self).get(self.autofire_mode_option_key) == "1":
            get_config(self).set(self.autofire_mode_option_key, "")
        else:
            get_config(self).set(self.autofire_mode_option_key, "1")

    def on_config(self, key, value):
        if key == "platform":
            self.layout.update()
            return

        if key == "amiga_model":
            value = get_config(self).get(
                "joystick_port_{0}_mode".format(self.port)
            )
            self.set_value_or_default(value)

        if key == self.mode_option_key or key == "amiga_model":
            value = DeviceManager.get_calculated_port_mode(
                get_config(self), self.port
            )
            for i, config in enumerate(self.joystick_mode_values):
                if config == value:
                    if self.mode_choice is not None:
                        self.mode_choice.set_index(i)
                        if self.port >= 4:
                            self.device_choice.set_enabled(i != 0)
                    break
            else:
                print("FIXME: could not set mode")
        elif key == self.device_option_key or key == "amiga_model":
            # print(self.joystick_values)
            value_lower = value.lower()
            for i, name in enumerate(self.joystick_values):
                if value_lower == name.lower():
                    self.device_choice.set_index(i)
                    break
        elif key == self.autofire_mode_option_key:
            if self.autofire_button is not None:
                if value == "1":
                    self.autofire_button.set_tooltip(
                        gettext("Auto-Fire is On")
                    )
                    self.autofire_button.set_icon_name(
                        "16x16/lightning_red.png"
                    )
                else:
                    self.autofire_button.set_tooltip(
                        gettext("Auto-Fire is Off")
                    )
                    self.autofire_button.set_icon_name(
                        "16x16/lightning_off.png"
                    )

        # this is intended to catch all config changes for all ports (both
        # mode and device) to update the defaults
        if key.startswith("joystick_port_") or key == "amiga_model":
            self.update_default_device()

    def on_device_list_updated_signal(self):
        # print(self.device_choice.index())
        had_default = self.device_choice.index() == 0
        self.rebuild_device_list()
        self.update_default_device(had_default=had_default)

    def on_settings_updated_signal(self):
        self.update_default_device()

    def update_default_device(self, had_default=None):
        config = {}
        for port in range(4):
            key = "joystick_port_{0}".format(port)
            if self.port == port:
                config[key] = ""
            else:
                config[key] = get_config(self).get(key)
            key = "joystick_port_{0}_mode".format(port)
            config[key] = DeviceManager.get_calculated_port_mode(
                get_config(self), port
            )
        device = DeviceManager.get_device_for_port(config, self.port)
        default_description = gettext("Default ({0})").format(
            fix_device_name(device.name)
        )
        # print("default_description = ", default_description)

        if had_default is None:
            had_default = self.device_choice.index() == 0
        # print("had default", had_default, self.device_choice.index())
        self.device_choice.set_item_text(0, default_description)
        # print("had_default", had_default)
        if had_default:
            # print("set text for", self.port, default_description)
            # self.device_choice.set_index(1)
            self.device_choice.set_text(default_description)
            self.device_choice.set_index(0)
            # print(self.device_choice.index())


class InputPortTypeChoice(fsui.Choice):
    def __init__(self, parent, port_gui_index):
        self._choice_values = []
        self._choice_labels = []
        self.port_gui_index = port_gui_index
        self.port = self.port_gui_index + 1
        super().__init__(parent, self._choice_labels)
        self._platform = ""
        self._config_key = ""
        config = get_config(self)
        self.on_config(Option.PLATFORM, config.get(Option.PLATFORM))
        self.changed.connect(self.__changed)
        self.set_min_width(MIN_TYPE_CHOICE_WIDTH)
        config.add_listener(self)

    def on_destroy(self):
        config = get_config(self)
        config.remove_listener(self)
        super().on_destroy()

    def __changed(self):
        config = get_config(self)
        config.set(self._config_key, self._choice_values[self.index()])

    def on_config(self, key, value):
        config = get_config(self)
        if key == Option.PLATFORM:
            self.port = self.port_gui_index + 1
            if value == Platform.C64:
                if self.port_gui_index == 0:
                    self.port = 2
                elif self.port_gui_index == 1:
                    self.port = 1
            self._platform = value
            self._config_key = "{}_port_{}_type".format(value, self.port)
            self.update_options()
            self.update_index(config.get(self._config_key))
            self.update_enabled()
        elif key == self._config_key:
            self.update_index(value)

    def update_enabled(self):
        self.set_visible(self._platform not in AMIGA_PLATFORMS)
        self.set_enabled(self._choice_labels != ["N/A"])

    def update_index(self, value):
        try:
            index = self._choice_values.index(value)
        except ValueError:
            index = 0
        with self.changed.inhibit:
            self.set_index(index)

    def update_options(self):
        try:
            option = Option.get(self._config_key)
        except KeyError:
            self._choice_values = ["0"]
            self._choice_labels = ["N/A"]
        else:
            choices = option["values"]
            self._choice_values = [x[0] for x in choices]
            self._choice_labels = [x[1] for x in choices]

            if "default" in option:
                for x in choices:
                    if x[0] == option["default"]:
                        default_label = x[1] + " (*)"
                        break
                else:
                    default_label = "??? (*)"
                self._choice_values.insert(0, "")
                self._choice_labels.insert(0, default_label)
        with self.changed.inhibit:
            self.clear()
            for label in self._choice_labels:
                self.add_item(label)


class InputPortDeviceChoice(fsui.ComboBox):
    def __init__(self, parent, port_gui_index):
        super().__init__(parent, [""], read_only=True)
        self.port_gui_index = port_gui_index
        self.port = self.port_gui_index + 1
        self._platform = ""
        self._config_key = ""
        self.device_option_key = ""

        # AmigaEnableBehavior(self.device_choice)
        self.device_values = []
        self.rebuild_device_list()

        config = get_config(self)
        # Must check platform before device option key
        self.on_config(Option.PLATFORM, config.get(Option.PLATFORM))
        self.on_config(
            self.device_option_key, config.get(self.device_option_key),
        )
        # self.changed.connect(self.__changed)
        self.set_index(0)

        config.add_listener(self)
        LauncherSignal.add_listener("settings_updated", self)
        LauncherSignal.add_listener("device_list_updated", self)

    def rebuild_device_list(self):
        self.device_values = ["", "none"]
        devices = ["", gettext("No Host Device")]
        for i, name in enumerate(DeviceManager.get_joystick_names()):
            devices.append(fix_device_name(name))
            self.device_values.append(DeviceManager.device_ids[i])
        self.set_items(devices)

    def on_destroy(self):
        config = get_config(self)
        config.remove_listener(self)
        LauncherSignal.remove_listener("settings_updated", self)
        LauncherSignal.remove_listener("device_list_updated", self)
        super().on_destroy()

    def on_changed(self):
        index = self.index()
        value = self.device_values[index]
        if value != "none":
            # Reset to default device for other ports using the same device.
            for port in range(1, 4 + 1):
                if self.port == port:
                    continue
                key = "{}_port_{}".format(self._platform, port)
                if get_config(self).get(key) == value:
                    get_config(self).set(key, "")
        get_config(self).set(self.device_option_key, value)

    def update_enabled(self):
        self.set_visible(self._platform not in AMIGA_PLATFORMS)
        # self.set_enabled(self._choice_labels != ["N/A"])

    def on_config(self, key, value):
        if key == "platform":
            self.port = self.port_gui_index + 1
            if value == Platform.C64:
                if self.port_gui_index == 0:
                    self.port = 2
                elif self.port_gui_index == 1:
                    self.port = 1
            self._platform = value
            self.update_enabled()
            self.device_option_key = "{}_port_{}".format(
                self._platform, self.port
            )
            # Disable the control if the type option does not exist
            try:
                Option.get("{}_port_{}_type".format(self._platform, self.port))
            except KeyError:
                self.set_enabled(False)
            else:
                self.set_enabled(True)

            return
        # if key == self.mode_option_key or key == "amiga_model":
        #     value = DeviceManager.get_calculated_port_mode(
        #         get_config(self), self.port)
        #     for i, config in enumerate(self.joystick_mode_values):
        #         if config == value:
        #             if self.mode_choice is not None:
        #                 self.mode_choice.set_index(i)
        #                 if self.port >= 4:
        #                     self.set_enabled(i != 0)
        #             break
        #     else:
        #         print("FIXME: could not set mode")
        # elif key == self.type_option_key:
        elif key == self.device_option_key:
            value_lower = value.lower()
            for i, name in enumerate(self.device_values):
                if value_lower == name.lower():
                    self.set_index(i)
                    break

        # This is intended to catch all config changes for all ports (both
        # mode and device) to update the defaults

        # FIXME:
        # if key.startswith("joystick_port_") or key == "amiga_model":
        #     self.update_default_device()

        if key.startswith("{}_port_".format(self._platform)):
            self.update_default_device()

    def on_device_list_updated_signal(self):
        # print(self.index())
        had_default = self.index() == 0
        self.rebuild_device_list()
        self.update_default_device(had_default=had_default)

    def on_settings_updated_signal(self):
        self.update_default_device()

    def update_default_device(self, had_default=None):
        config = {"platform": self._platform}
        for port in range(1, 4 + 1):
            key = "{}_port_{}".format(self._platform, port)
            if self.port == port:
                config[key] = ""
            else:
                config[key] = get_config(self).get(key)
            key = "{}_port_{}_type".format(self._platform, port)
            config[key] = get_config(self).get(key)
            # config[key] = DeviceManager.get_calculated_port_mode(
            #     get_config(self), port)

        device = DeviceManager.get_non_amiga_device_for_port(config, self.port)

        default_description = "{} (*)".format(fix_device_name(device.name))
        # print("default_description = ", default_description)

        if had_default is None:
            had_default = self.index() == 0
        # print("had default", had_default, self.index())
        self.set_item_text(0, default_description)
        # print("had_default", had_default)
        if had_default:
            # print("set text for", self.port, default_description)
            # self.set_index(1)
            self.set_text(default_description)
            self.set_index(0)
            # print(self.index())


def fix_device_name(name):
    system = gettext("System")
    if sys.platform == "win32":
        system = "Windows"
    elif sys.platform.startswith("linux"):
        system = "Linux"
    elif sys.platform == "darwin":
        system = "OS X"

    if name == "Keyboard":
        return gettext("{system} Keyboard").format(system=system)
    elif name == "Mouse":
        return gettext("Mouse: {system} Mouse").format(system=system)
    else:
        return gettext(name)
