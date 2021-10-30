from typing import Dict, List, Optional, Tuple

from fsgamesys import Option
from fsgamesys.drivers.gamedriver import Port
from fsgamesys.input.inputdevice import InputDevice
from fsgamesys.input.inputservice import useInputService
from launcher.devicemanager import DeviceManager

# from .device import Device


class EnumerateHelper(object):
    def __init__(self):
        self.devices: List[InputDevice] = []
        self.joystick_devices: List[InputDevice] = []
        self.keyboard_devices: List[InputDevice] = []
        self.joystick_like_devices: List[InputDevice] = []
        self.initialized = False

    def update(self):
        # if cls.initialized:
        #     return
        # init can be called more than once (by setting initialized to
        # false, used by refresh function, so we need to clear the lists...
        self.devices = []
        self.joystick_devices = []
        self.keyboard_devices = []
        self.joystick_like_devices = []
        self.init_2()
        self.initialized = True

    def init(self) -> None:
        if self.initialized:
            return
        self.init_2()
        self.initialized = True

    def init_2(self) -> None:
        inputService = useInputService()
        for device in inputService.getJoysticks():
            self.devices.append(device)
            self.joystick_devices.append(device)
            self.joystick_like_devices.append(device)
        for device in inputService.getKeyboard():
            self.devices.append(device)
            self.joystick_like_devices.append(device)
        for device in inputService.getMice():
            self.devices.append(device)

    def default_port_selection(
        self, ports: List[Port], options: Dict[str, str]
    ) -> None:
        print("[INPUT] Default port selection (EnumerateHelper)")
        self.init()
        # for device in self.devices:
        #     print(" #", device.id)
        #     device.configure("megadrive")

        if len(ports) > 0:
            if ports[0].type_option:
                print("[INPUT] New-style port device selection:")
                # Supports new-style port selection
                port_devices = DeviceManager.get_non_amiga_devices_for_ports(
                    options
                )

                if ports[0].type_option == Option.C64_PORT_2_TYPE:
                    print("[INPUT] Hack for inverted C64 port order")
                    temp = port_devices[1]
                    port_devices[1] = port_devices[2]
                    port_devices[2] = temp
                for i, port in enumerate(ports):
                    print("[INPUT]  xxxx ", self.devices)
                    for device in self.devices:
                        print(
                            "[INPUT]", port_devices[i + 1].id, "vs", device.id
                        )
                        if port_devices[i + 1].id == device.id:
                            port.device = device
                            print("[INPUT]", port.name, "<-", device.id)
                            break
                    else:
                        print("[INPUT]", port.name, "<- [None]")
                return

        joystick_like_devices = self.joystick_like_devices[:]
        print("[INPUT] Old-style port device selection:")
        for port in ports:
            for i, device in enumerate(joystick_like_devices):
                # device.configure()
                if True:
                    joystick_like_devices.pop(i)
                    port.device = device
                    break
            print("[INPUT] Old Selection:", port.name, port.device)
