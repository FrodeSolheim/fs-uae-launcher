from fscore.types import SimpleCallable
from typing import List, Optional

from fsgamesys.input2.dataclasses import InputDevice

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

    def _createJoystickDevice(self) -> InputDevice:
        # FIXME: Should ID be lowercase?
        return InputDevice(
            type="joystick",
            id="Xbox 360 Controller",
            name="Xbox 360 Controller",
        )

    def getInputDevices(self) -> List[InputDevice]:
        if len(self.devices) == 0:
            self._updateDeviceListNow()
        # return self.devices.copy()
        return self.devices.copy()

    def refreshDeviceList(self) -> None:
        pass

    def removeDevicesChangedListener(self, listener: SimpleCallable) -> None:
        self.devicesChangedListeners.remove(listener)

    def _updateDeviceListNow(self):
        devices: List[InputDevice] = []
        devices.append(self._createNoneDevice())
        devices.append(self._createKeyboardDevice())
        devices.append(self._createMouseDevice())
        devices.append(self._createJoystickDevice())

        self.devices = devices
