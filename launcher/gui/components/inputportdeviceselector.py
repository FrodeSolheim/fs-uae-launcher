from typing import Dict, Optional

import fsui
from fsgamesys.platforms.platform import Platform
from fswidgets.widget import Widget
from launcher.context import get_config, useInputService
from launcher.devicemanager import DeviceManager
from launcher.launcher_signal import LauncherSignal
from launcher.option import Option


class InputPortDeviceSelector(fsui.ComboBox):
    def __init__(self, parent: Widget, port_gui_index: int):
        super().__init__(parent, [""], read_only=True)
        self.port_gui_index = port_gui_index
        # self.port = self.port_gui_index + 1

        config = get_config(self)
        self._platform = config.get(Option.PLATFORM)
        self.port = self.convertIndexToPortNumber(self.port_gui_index)

        self._config_key = ""
        # FIXME: Remove self.deviceKey
        self.deviceKey = "" # self.getDeviceKey(self.port)

        # AmigaEnableBehavior(self.device_choice)
        self.device_values = []

        self.inputService = useInputService()
        self.rebuildDeviceList()

        # Must check platform before device option key
        self.on_config(Option.PLATFORM, config.get(Option.PLATFORM))
        self.on_config(self.deviceKey, config.get(self.deviceKey))
        # self.changed.connect(self.__changed)
        self.setIndex(0)

        config.add_listener(self)
        LauncherSignal.add_listener("settings_updated", self)
        # FIXME: Soon not needed
        LauncherSignal.add_listener("device_list_updated", self)

        self.inputService.addDevicesChangedListener(self.onDevicesChanged)

    def onDestroy(self):
        super().onDestroy()
        self.inputService.removeDevicesChangedListener(self.onDevicesChanged)

        config = get_config(self)
        config.remove_listener(self)
        LauncherSignal.remove_listener("settings_updated", self)
        # FIXME: Soon not needed
        LauncherSignal.remove_listener("device_list_updated", self)

    def onDevicesChanged(self):
        pass

    # -------------------------------------------------------------------------

    def rebuildDeviceList(self):
        # self.device_values = ["", "none"]
        self.device_values = [""]
        # devices = ["", gettext("No Host Device")]
        devices = [""]
        # for i, name in enumerate(DeviceManager.get_joystick_names()):
        #     devices.append(fixDeviceName(name))
        #     self.device_values.append(DeviceManager.device_ids[i])
        for device in self.inputService.getInputDevices():
            # devices.append(fixDeviceName(device.name))
            devices.append(device.name)
            self.device_values.append(device.id)
        self.setItems(devices)

    def on_changed(self):
        index = self.index()
        value = self.device_values[index]
        if value != "none":
            # Reset to default device for other ports using the same device.
            for i in range(4):
                portNumber = self.convertIndexToPortNumber(i)
                if self.port == portNumber:
                    continue
                key = self.getDeviceKey(portNumber)
                print("on_changed", key, "?=", value, get_config(self).get(key))
                # key = "{}_port_{}".format(self._platform, port)
                if get_config(self).get(key) == value:
                    get_config(self).set(key, "")
        # print("set", self.getDeviceKey(self.port), "to", value)
        # get_config(self).set(self.getDeviceKey(self.port), value)
        print("set", self.deviceKey, "to", value)
        get_config(self).set(self.deviceKey, value)

    def update_enabled(self):
        # self.setVisible(self._platform not in AMIGA_PLATFORMS)
        # # self.set_enabled(self._choice_labels != ["N/A"])
        pass

    def on_config(self, key: str, value: str):
        if key == "platform":
            self._platform = value
            # This must be called after self._platform ha been set
            self.port = self.convertIndexToPortNumber(self.port_gui_index)
            self.deviceKey = self.getDeviceKey(self.port)

            self.update_enabled()
            # FIXME: Update for Amiga!
            # self.deviceKey = "{}_port_{}".format(self._platform, self.port)
            # Disable the control if the type option does not exist
            try:
                # Option.get("{}_port_{}_type".format(self._platform, self.port))
                Option.get(self.getModeKey(self.port))
            except KeyError:
                self.disable()
            else:
                self.enable()

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
        elif key == self.deviceKey:
            value_lower = value.lower()
            for i, name in enumerate(self.device_values):
                if value_lower == name.lower():
                    self.setIndex(i)
                    break

        # This is intended to catch all config changes for all ports (both
        # mode and device) to update the defaults

        # FIXME:
        # if key.startswith("joystick_port_") or key == "amiga_model":
        #     self.updateDefaultDevice()

        # this is intended to catch all config changes for all ports (both
        # mode and device) to update the defaults
        if self.isAmiga():
            if key.startswith("joystick_port_") or key == "amiga_model":
                self.updateDefaultDevice()
        else:
            if key.startswith("{}_port_".format(self._platform)):
                self.updateDefaultDevice()

    def on_device_list_updated_signal(self):
        # print(self.index())
        wasDefault = self.index() == 0
        self.rebuildDeviceList()
        self.updateDefaultDevice(wasDefault=wasDefault)

    def on_settings_updated_signal(self):
        self.updateDefaultDevice()

    def isAmiga(self) -> bool:
        return self._platform.lower() in ["", "amiga", "cdtv", "cd32"]

    def getDeviceKey(self, portNumber: int):
        if self.isAmiga():
            return "joystick_port_{0}".format(portNumber)
        else:
            return "{}_port_{}".format(self._platform, portNumber)

    def getModeKey(self, portNumber: int):
        if self.isAmiga():
            return "joystick_port_{0}_mode".format(portNumber)
        else:
            return "{}_port_{}_type".format(self._platform, portNumber)

    def getDeviceForPort(self, config: Dict[str, str]):
        if self.isAmiga():
            device = DeviceManager.get_device_for_port(config, self.port)
        else:
            device = DeviceManager.get_non_amiga_device_for_port(
                config, self.port
            )
        return device

    def convertIndexToPortNumber(self, index: int):
        if self.isAmiga():
            if index == 0:
                return 1
            elif index == 1:
                return 0
            else:
                return index
        elif self._platform == Platform.C64:
            if index == 0:
                return 2
            elif index == 1:
                return 1
        return index + 1

    def updateDefaultDevice(self, wasDefault: Optional[bool] = None):
        isAmiga = self.isAmiga()
        config = {"platform": self._platform}
        for i in range(4):
            portNumber = self.convertIndexToPortNumber(i)
            deviceKey = self.getDeviceKey(portNumber)
            if self.port == portNumber:
                config[deviceKey] = ""
            else:
                config[deviceKey] = get_config(self).get(deviceKey)
            modeKey = self.getModeKey(portNumber)
            if isAmiga:
                config[modeKey] = DeviceManager.get_calculated_port_mode(
                    get_config(self), portNumber
                )
            else:
                config[modeKey] = get_config(self).get(modeKey)
            # config[key] = DeviceManager.get_calculated_port_mode(
            #     get_config(self), port)

        device = self.getDeviceForPort(config)

        # defaultDescription = "{} (*)".format(fixDeviceName(device.name))
        defaultDescription = f"{device.name} (*)"
        # print("default_description = ", default_description)
        if wasDefault is None:
            wasDefault = self.index() == 0
        self.set_item_text(0, defaultDescription)
        if wasDefault:
            self.setText(defaultDescription)
            self.setIndex(0)
