from typing import List, Optional

from fscore.types import SimpleCallable
from fsgamesys.input2.dataclasses import InputDevice
from fsgamesys.input.device import Device
from fsgamesys.input.devicemanager import DeviceManager

# FIXME: Suspend InputService polling/waiting on device updates while
# emulation is running


class InputService:
    _instance: Optional["InputService"] = None

    @classmethod
    def getInstance(cls) -> "InputService":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self.devicesChangedListeners: List[SimpleCallable] = []
        self.devices: List[InputDevice] = []

    def addDevicesChangedListener(self, listener: SimpleCallable) -> None:
        self.devicesChangedListeners.append(listener)

    def _createNoneDevice(self) -> InputDevice:
        # FIXME: Should ID be lowercase?
        return InputDevice(type="none", id="none", name="No Host Device")

    def _createKeyboardDevice(self) -> InputDevice:
        # FIXME: Should ID be lowercase?
        return InputDevice(type="keyboard", id="Keyboard", name="Keyboard")

    def _createMouseDevice(self) -> InputDevice:
        # FIXME: Should ID be lowercase?
        return InputDevice(type="mouse", id="Mouse", name="Mouse")

    # def _createJoystickDevice(self) -> InputDevice:
    #     # FIXME: Should ID be lowercase?
    #     return InputDevice(
    #         type="joystick",
    #         id="Xbox 360 Controller",
    #         name="Xbox 360 Controller",
    #     )

    def getDevice(self, deviceId: str):
        for device in self.devices:
            if device.id == deviceId:
                return device
        # raise LookupError("Device not found")
        return None

    # FIXME: Rename to getDevices
    def getInputDevices(self) -> List[InputDevice]:
        if len(self.devices) == 0:
            self._updateDeviceListNow()
        # return self.devices.copy()
        return self.devices.copy()

    def refreshDeviceList(self) -> None:
        self._updateDeviceListNow()

    def removeDevicesChangedListener(self, listener: SimpleCallable) -> None:
        self.devicesChangedListeners.remove(listener)

    def _createJoystickDeviceFromLegacy(self, device: Device) -> InputDevice:
        # FIXME: Should ID be lowercase?
        return InputDevice(
            type="joystick",
            # id="Xbox 360 Controller",
            id=device.id,
            name=device.name,
            axisCount=device.axes,
            buttonCount=device.buttons,
            hatCount=device.hats,
        )

    def _updateDeviceListNow(self):
        devices: List[InputDevice] = []
        devices.append(self._createNoneDevice())
        devices.append(self._createKeyboardDevice())
        devices.append(self._createMouseDevice())
        # devices.append(self._createJoystickDevice())

        # Using legacy DeviceManager for now...
        for device in DeviceManager.instance().get_devices(refresh=True):
            if device.type == "joystick":
                print(device)
                devices.append(self._createJoystickDeviceFromLegacy(device))

        self.devices = devices
        print("\n\n\n\n\nnew device list", devices)
