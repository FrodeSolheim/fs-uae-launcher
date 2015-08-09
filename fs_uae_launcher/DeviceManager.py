import sys
import re
import traceback
import subprocess
from .I18N import gettext
from .Settings import Settings
from .Signal import Signal
from fsgs.amiga.FSUAEDeviceHelper import FSUAEDeviceHelper


def create_cmp_id(id):
    return id.lower().replace(" ", "")


class Device:

    def __init__(self, id, name, type):
        self.id = id
        self.name = name
        self.type = type
        self.port = None
        self.cmp_id = create_cmp_id(id)


class DeviceManager:

    initialized = False
    devices = []
    device_ids = []
    device_names = []
    device_types = []
    device_name_count = {}

    joystick_data = {}

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

        cls.devices.append(Device("none", gettext("No Device"), "none"))
        # cls.devices.append(Device("mouse", _("Mouse"), "mouse"))
        cls.init_fsuae()
        for id, name, type in zip(cls.device_ids, cls.device_names,
                                  cls.device_types):
            cls.devices.append(Device(id, name, type))
        # cls.devices.append(
        #     Device("keyboard", _("Cursor Keys and Right Ctrl/Alt"),
        #            "joystick"))
        cls.initialized = True

    @classmethod
    def refresh(cls):
        cls.initialized = False
        cls.init()
        Signal.broadcast("device_list_updated")

    @classmethod
    def init_fsuae(cls):
        print("finding connected joysticks")
        try:
            p = FSUAEDeviceHelper.start_with_args(
                ["--list"], stdout=subprocess.PIPE)
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
                cls.joystick_data[last_joystick] = \
                    buttons, hats, axes, balls, guid

                continue
            device_type, name = line.split(" ", 1)
            # if name.lower() in ["keyboard", "mouse"]:
            #     # these are automatically added
            #     continue
            name_count = cls.device_name_count.get(name, 0) + 1
            cls.device_name_count[name] = name_count
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
            cls.joystick_data["Dummy Joystick"] = \
                1, 0, 2, 0, "c6c1bc29b0124fe6890757bb09ef006f"

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
    def is_joystick(cls, device):
        return cls.get_device_type(device) == "joystick"

    @classmethod
    def get_joystick_ids(cls):
        cls.init()
        return cls.device_ids[:]

    @classmethod
    def get_preferred_joysticks(cls):
        prefs = []
        if Settings.get("primary_joystick"):
            prefs.append(create_cmp_id(Settings.get("primary_joystick")))
        if Settings.get("secondary_joystick"):
            prefs.append(create_cmp_id(Settings.get("secondary_joystick")))
        return prefs

    @classmethod
    def get_preferred_gamepads(cls):
        return cls.get_preferred_joysticks()

    @classmethod
    def get_calculated_port_mode(cls, config, port):
        value = config.get("joystick_port_{0}_mode".format(port))
        if not value:
            if port == 0:
                return "mouse"
            elif port == 1:
                if config.get("amiga_model").startswith("CD32"):
                    return "cd32 gamepad"
                else:
                    return "joystick"
            return "nothing"
        return value

    @classmethod
    def get_devices_for_ports(cls, config):
        cls.init()
        ports = [cls.devices[0] for _ in range(5)]
        for device in cls.devices:
            device.port = None
        for p in range(4):
            key = "joystick_port_{0}".format(p)
            value = config.get(key)
            for device in cls.devices:
                if device.id == value:
                    device.port = p
                    break
        # print("-")
        # for device in cls.devices:
        #     print(device.port, device.id)
        # print("-")

        def autofill(port, type):
            mode = config.get("joystick_port_{0}_mode".format(port))
            if not mode:
                mode = cls.get_calculated_port_mode(config, port)
            value = config.get("joystick_port_{0}".format(port))
            if value:
                # specific device chosen
                for device in cls.devices:
                    if device.id == value:
                        ports[port] = device
                        break
                return
            if type == "mouse":
                # print("a", mode)
                if mode != "mouse":
                    return
                # print("b")
                for device in cls.devices:
                    # print("c")
                    if device.type == "mouse" and device.port is None:
                        # print("d")
                        ports[port] = device
                        device.port = port
                        return
            elif type == "joystick":
                if mode == "cd32 gamepad":
                    prefs = cls.get_preferred_joysticks()
                elif mode == "joystick":
                    prefs = cls.get_preferred_gamepads()
                else:
                    return
                # try to find an available preferred device first
                for pref in prefs:
                    for device in cls.devices:
                        if device.cmp_id == pref and device.port is None:
                            ports[port] = device
                            device.port = port
                            return
                # find first suitable device
                for device in cls.devices:
                    if device.type == "joystick" and device.port is None:
                        ports[port] = device
                        device.port = port
                        return
                for device in cls.devices:
                    if device.type == "keyboard" and device.port is None:
                        ports[port] = device
                        device.port = port
                        return

        for p in [0, 1, 2, 3]:
            autofill(p, "mouse")
        for p in [1, 0, 3, 2]:
            autofill(p, "joystick")
        return ports

    @classmethod
    def get_device_for_port(cls, config, port):
        return cls.get_devices_for_ports(config)[port]
