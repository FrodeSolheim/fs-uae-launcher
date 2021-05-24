import re
import subprocess
import traceback
from typing import Dict, List, Optional, Tuple

from fsgamesys import Option
from fsgamesys.amiga.fsuaedevicehelper import FSUAEDeviceHelper
from launcher.devicemanager import DeviceManager

from .device import Device


class EnumerateHelper(object):
    def __init__(self):
        self.devices: List[Device] = []
        self.joystick_devices: List[Device] = []
        self.keyboard_devices: List[Device] = []
        self.joystick_like_devices: List[Device] = []
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
        self.init_fsuae()
        self.initialized = True

    def init(self):
        if self.initialized:
            return
        self.init_fsuae()
        self.initialized = True

    def init_fsuae(self):
        print("[INPUT] EnumerateHelper: Finding connected joysticks")
        try:
            p = FSUAEDeviceHelper.start_with_args(
                ["--list"], stdout=subprocess.PIPE
            )
            assert p.stdout is not None
            joysticks = p.stdout.read()
            p.wait()
        except Exception:
            print("[INPUT] Exception while listing joysticks and devices")
            traceback.print_exc()
            return
        print("[INPUT]", repr(joysticks))
        # If the character conversion fails, replace will ensure that
        # as much as possible succeeds. The joystick in question will
        # not be pre-selectable in the launcher, but the other ones will
        # work at least.
        joysticks = joysticks.decode("UTF-8", "replace")
        joysticks = [x.strip() for x in joysticks.split("\n") if x.strip()]

        # joysticks.append("J: controller xbox 360 for windows")
        # joysticks.append("Buttons: 10 Hats: 1 Axes: 5 Balls: 0")

        device_name_count: Dict[Tuple[str, str], int] = {}
        last_joystick: Device = Device()

        for line in joysticks:
            if line.startswith("#"):
                continue
            elif line.startswith("Buttons:"):
                parts = line.split(" ")
                last_joystick.buttons = int(parts[1])
                last_joystick.hats = int(parts[3])
                last_joystick.axes = int(parts[5])
                last_joystick.balls = int(parts[7])
                continue
            elif line.startswith("SDLName:"):
                value = line.split(" ", 1)[1]
                # Strip quotes
                last_joystick.sdl_name = value[1:-1]
                continue

            device = Device()
            device_type, name = line.split(" ", 1)

            name_count = device_name_count.get((device_type, name), 0) + 1
            device_name_count[(device_type, name)] = name_count
            if name_count > 1:
                name = name + " #" + str(name_count)
            device.id = name
            name = re.sub("[ ]+", " ", name)
            device.name = name
            if device_type == "J:":
                device.type = "joystick"
                last_joystick = device
                self.joystick_devices.append(device)
            elif device_type == "M:":
                device.type = "mouse"
            elif device_type == "K:":
                # works as an emulated joystick...
                # device_type = "joystick"
                device.type = "keyboard"
                self.keyboard_devices.append(device)
            # self.device_types.append(device_type)
            self.devices.append(device)
        for i, device in enumerate(self.joystick_devices):
            device.index = i
        for i, device in enumerate(self.keyboard_devices):
            device.index = i

        self.joystick_like_devices.extend(self.joystick_devices)
        self.joystick_like_devices.extend(self.keyboard_devices)

    def default_port_selection(self, ports, options):
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
                    for device in self.devices:
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
