import re
import subprocess
import sys
import traceback
from typing import Dict, List

from fsgamesys.amiga.fsuaedevicehelper import FSUAEDeviceHelper
from launcher.context import useInputService
from launcher.i18n import gettext
from launcher.launcher_settings import LauncherSettings
from launcher.launcher_signal import LauncherSignal
from launcher.option import Option


class Device:
    def __init__(self, id: str, name: str, type: str):
        self.id = id
        self.name = name
        self.type = type
        self.port = None
        self.cmp_id = Device.create_cmp_id(id)

    @staticmethod
    def create_cmp_id(id_: str) -> str:
        return id_.lower().replace(" ", "")

    def __repr__(self):
        return "<Device {}".format(self.id)


class DeviceManager:
    initialized = False
    devices = []
    device_ids = []
    device_names = []
    device_types = []
    device_name_count = {}

    joystick_data = {}
    sdl_names = {}

    @classmethod
    def joystick_buttons(cls, device):
        return cls.joystick_data[device][0]

    @classmethod
    def joystick_hats(cls, device):
        return cls.joystick_data[device][1]

    @classmethod
    def joystick_axes(cls, device):
        return cls.joystick_data[device][2]

    @classmethod
    def joystick_balls(cls, device):
        return cls.joystick_data[device][3]

    @classmethod
    def joystick_guid(cls, device):
        return cls.joystick_data[device][4]

    @classmethod
    def joystick_sdl_name(cls, device):
        return cls.sdl_names[device]

    @classmethod
    def init(cls):
        if cls.initialized:
            return
        # init can be called more than once (by setting initialized to
        # false, used by refresh function, so we need to clear the lists...
        cls.devices = []
        cls.device_ids = []
        cls.device_names = []
        cls.device_types = []
        cls.device_name_count = {}

        cls.devices.append(Device("none", gettext("No Host Device"), "none"))
        # cls.devices.append(Device("mouse", _("Mouse"), "mouse"))
        cls.init_fsuae()
        for id, name, type in zip(
            cls.device_ids, cls.device_names, cls.device_types
        ):
            cls.devices.append(Device(id, name, type))
        # cls.devices.append(
        #     Device("keyboard", _("Cursor Keys and Right Ctrl/Alt"),
        #            "joystick"))
        cls.initialized = True

    @classmethod
    def refresh(cls):
        cls.initialized = False

        # FIXME: Not using DeviceManager anymore, really...
        # cls.init()

        # FIXME: REPLACE WITH EnumerateHelper!!!

        # LauncherSignal.broadcast("device_list_updated")

    @classmethod
    def init_fsuae(cls):
        print("DeviceManager: finding connected joysticks")
        try:
            p = FSUAEDeviceHelper.start_with_args(
                ["--list"], stdout=subprocess.PIPE
            )
            assert p.stdout
            joysticks = p.stdout.read()
            p.wait()
        except Exception:
            print("exception while listing joysticks and devices")
            traceback.print_exc()
            return
        print(repr(joysticks))
        # If the character conversion fails, replace will ensure that
        # as much as possible succeeds. The joystick in question will
        # not be pre-selectable in the launcher, but the other ones will
        # work at least.
        joysticks = joysticks.decode("UTF-8", "replace")
        joysticks = [x.strip() for x in joysticks.split("\n") if x.strip()]
        last_joystick = ""
        for line in joysticks:
            if line.startswith("#"):
                continue
            if line.startswith("Buttons:"):
                parts = line.split(" ")
                buttons = int(parts[1])
                hats = int(parts[3])
                axes = int(parts[5])
                balls = int(parts[7])
                guid = parts[9]
                cls.joystick_data[last_joystick] = (
                    buttons,
                    hats,
                    axes,
                    balls,
                    guid,
                )
                continue
            if line.startswith("SDLName: "):
                value = line[len("SDLName: ") :]
                # Strip quotes
                cls.sdl_names[last_joystick] = value[1:-1]
                # print("\n\n\n\n\n", line)
                # print(last_joystick, "<-", value[1:-1])
                # print("\n")

            device_type, name = line.split(" ", 1)
            # if name.lower() in ["keyboard", "mouse"]:
            #     # these are automatically added
            #     continue
            name_count = cls.device_name_count.get((device_type, name), 0) + 1
            cls.device_name_count[(device_type, name)] = name_count
            if name_count > 1:
                name = name + " #" + str(name_count)
            cls.device_ids.append(name)
            name = re.sub("[ ]+", " ", name)
            cls.device_names.append(name)
            if device_type == "J:":
                device_type = "joystick"
                last_joystick = name
            elif device_type == "M:":
                device_type = "mouse"
            elif device_type == "K:":
                # works as an emulated joystick...
                # device_type = "joystick"
                device_type = "keyboard"
            cls.device_types.append(device_type)

        if "--add-dummy-joystick" in sys.argv:
            cls.device_ids.append("Dummy Joystick")
            cls.device_names.append("Dummy Joystick")
            cls.device_types.append("joystick")
            cls.joystick_data["Dummy Joystick"] = (
                1,
                0,
                2,
                0,
                "c6c1bc29b0124fe6890757bb09ef006f",
            )

    @classmethod
    def get_joystick_names(cls):
        cls.init()
        return cls.device_names[:]

    @classmethod
    def get_device_type(cls, device):
        cls.init()
        for i in range(len(cls.device_names)):
            if cls.device_names[i] == device:
                return cls.device_types[i]
        return ""

    @classmethod
    def is_joystick(cls, device: str) -> bool:
        return cls.get_device_type(device) == "joystick"

    @classmethod
    def get_joystick_ids(cls) -> List[str]:
        cls.init()
        return cls.device_ids[:]

    @classmethod
    def get_preferred_joysticks(cls) -> List[str]:
        prefs: List[str] = []
        if LauncherSettings.get("primary_joystick"):
            prefs.append(
                Device.create_cmp_id(LauncherSettings.get("primary_joystick"))
            )
        if LauncherSettings.get("secondary_joystick"):
            prefs.append(
                Device.create_cmp_id(
                    LauncherSettings.get("secondary_joystick")
                )
            )
        return prefs

    @classmethod
    def get_preferred_gamepads(cls) -> List[str]:
        return cls.get_preferred_joysticks()

    @classmethod
    def get_calculated_port_mode(
        cls, config: Dict[str, str], port: int
    ) -> str:
        value = config.get("joystick_port_{0}_mode".format(port))
        if not value:
            if port == 0:
                return "mouse"
            elif port == 1:
                if config.get("amiga_model", "").startswith("CD32"):
                    return "cd32 gamepad"
                else:
                    return "joystick"
            return "nothing"
        return value

    @classmethod
    def get_devices_for_ports(cls, config: Dict[str, str]):
        # cls.init()
        inputService = useInputService()
        devices = inputService.getInputDevices()
        ports = [devices[0] for _ in range(5)]
        for device in devices:
            device.port = None
        for p in range(4):
            key = "joystick_port_{0}".format(p)
            value = config.get(key)
            for device in devices:
                if device.id == value:
                    device.port = p
                    break

        # print("-")
        # for device in cls.devices:
        #     print(device.port, device.id)
        # print("-")

        def auto_fill(port: int, type: str):
            mode = config.get("joystick_port_{0}_mode".format(port))
            if not mode:
                mode = cls.get_calculated_port_mode(config, port)
            val = config.get("joystick_port_{0}".format(port))
            if val:
                # specific device chosen
                for dev in devices:
                    if dev.id == val:
                        ports[port] = dev
                        break
                return
            if type == "mouse":
                # print("a", mode)
                if mode != "mouse":
                    return
                # print("b")
                for dev in devices:
                    # print("c")
                    if dev.type == "mouse" and dev.port is None:
                        # print("d")
                        ports[port] = dev
                        dev.port = port
                        return
            elif type == "joystick":
                if mode == "cd32 gamepad":
                    prefs = cls.get_preferred_gamepads()
                elif mode == "joystick":
                    prefs = cls.get_preferred_joysticks()
                else:
                    return
                # try to find an available preferred device first
                for pref in prefs:
                    for dev in devices:
                        if (
                            Device.create_cmp_id(dev.id) == pref
                            and dev.port is None
                        ):
                            ports[port] = dev
                            dev.port = port
                            return
                # find first suitable device
                for dev in devices:
                    if dev.type == "joystick" and dev.port is None:
                        ports[port] = dev
                        dev.port = port
                        return
                for dev in devices:
                    if dev.type == "keyboard" and dev.port is None:
                        ports[port] = dev
                        dev.port = port
                        return

        for p in [0, 1, 2, 3]:
            auto_fill(p, "mouse")
        for p in [1, 0, 3, 2]:
            auto_fill(p, "joystick")
        return ports

    @classmethod
    def get_device_for_port(cls, config: Dict[str, str], port: int):
        return cls.get_devices_for_ports(config)[port]

    @classmethod
    def get_non_amiga_devices_for_ports(cls, config: Dict[str, str]):
        platform = config.get("platform")
        # cls.init()
        inputService = useInputService()
        devices = inputService.getInputDevices()
        # Launcher has 5 input devices in total (4 + 1 virtual)
        # ports = [cls.devices[0] for _ in range(5)]
        # + 1 dummy device for index 0
        ports = [devices[0] for _ in range(6)]

        for device in devices:
            device.port = None
        for port_ in range(1, 4 + 1):
            key = "{}_port_{}".format(platform, port_)
            value = config.get(key)
            print(key, value)
            for device in devices:
                if device.id == value:
                    device.port = port_
                    break

        print("before auto-fill")
        print(ports)

        # print("-")
        # for device in cls.devices:
        #     print(device.port, device.id)
        # print("-")

        def auto_fill(port: int, type: str):
            mode = config.get("{}_port_{}_type".format(platform, port))
            if not mode:
                # FIXME: DEFAULT
                # mode = cls.get_calculated_port_mode(config, port)
                # mode = "gamepad"
                try:
                    option = Option.get(
                        "{}_port_{}_type".format(platform, port)
                    )
                    mode = option["default"]
                except KeyError:
                    # FIXME: How to handle?
                    mode = ""

            print("mode for", port, "is", mode)
            if cls.is_mouse_device(mode):
                mode = "mouse"

            val = config.get("{}_port_{}".format(platform, port))
            if val:
                # specific device chosen
                for dev in devices:
                    if dev.id == val:
                        ports[port] = dev
                        break
                return

            if type == "mouse":
                # print("a", mode)
                if mode != "mouse":
                    return
                # print("b")
                for dev in devices:
                    # print("c")
                    if dev.type == "mouse" and dev.port is None:
                        # print("d")
                        ports[port] = dev
                        dev.port = port
                        return
            elif type == "joystick":
                if mode == "none":
                    return
                elif mode == "mouse":
                    return
                # elif mode == "gamepad":
                #     prefs = cls.get_preferred_gamepads()
                # elif mode == "joystick":
                #     prefs = cls.get_preferred_joysticks()
                # else:
                #     return

                prefs = cls.get_preferred_gamepads()

                # try to find an available preferred device first
                for pref in prefs:
                    for dev in devices:
                        if (
                            Device.create_cmp_id(dev.id) == pref
                            and dev.port is None
                        ):
                            ports[port] = dev
                            dev.port = port
                            return
                # find first suitable device
                for dev in devices:
                    if dev.type == "joystick" and dev.port is None:
                        ports[port] = dev
                        dev.port = port
                        return
                for dev in devices:
                    if dev.type == "keyboard" and dev.port is None:
                        ports[port] = dev
                        dev.port = port
                        return

        for p in [1, 2, 3, 4]:
            auto_fill(p, "mouse")
        # FIXME: Hack, circular dependency
        from fsgamesys.platforms.platform import Platform

        if platform == Platform.C64:
            port_order = [2, 1, 3, 4]
        else:
            port_order = [1, 2, 3, 4]
        for p in port_order:
            auto_fill(p, "joystick")
            print("auto-fill", p, "=", ports[p])
        return ports

    @classmethod
    def get_non_amiga_device_for_port(cls, config: Dict[str, str], port: int):
        ports = cls.get_non_amiga_devices_for_ports(config)
        print(ports, port)
        return ports[port]

    @classmethod
    def is_mouse_device(cls, type_: str):
        # FIXME: Should be put in platform-specific code, here for now.
        return type_ in [
            "mouse",  # Amiga, ...
            "zapper",  # NES
            "arkanoid",  # NES
        ]
