import os

from fsgamesys.drivers.dolphindriver import DolphinDriver, DolphinInputMapper
from fsgamesys.platforms.platform import Platform
from fsgamesys.platforms.loader import SimpleLoader

NGC_PLATFORM_NAME = "GameCube"
NGC_CONTROLLER = {
    "type": "gamepad",
    "description": "Gamepad",
    "mapping_name": "ngc",
}


class GameCubePlatform(Platform):
    # FIXME: Move to init instead
    PLATFORM_NAME = NGC_PLATFORM_NAME

    def driver(self, fsgc):
        return GameCubeDriver(fsgc)

    def loader(self, fsgc):
        return GameCubeLoader(fsgc)


class GameCubeLoader(SimpleLoader):
    pass


class GameCubeDriver(DolphinDriver):
    PORTS = [
        {"description": "Controller 1", "types": [NGC_CONTROLLER]},
        {"description": "Controller 2", "types": [NGC_CONTROLLER]},
        {"description": "Controller 3", "types": [NGC_CONTROLLER]},
        {"description": "Controller 4", "types": [NGC_CONTROLLER]},
    ]

    def __init__(self, fsgs):
        super().__init__(fsgs)
        self.helper = GameCubeHelper(self.options)

    def dolphin_configure_core(self, f):
        # find devices now (need to know how many devices to
        # specify in dolphin.ini)
        # devices = self.context.input.get_devices(1, 4)
        # configure dolphin.ini
        device_count = 0
        for i, port in enumerate(self.ports):
            if port.device:
                device_count += 1
        for i in range(device_count):
            f.write("SIDevice{0} = 150994944\n".format(i))

        # FIXME:
        memcard_region = "USA"

        f.write(
            "MemcardA = {dir}/MemoryCardA.{region}.raw\n".format(
                dir=self.get_state_dir(), region=memcard_region
            )
        )
        f.write(
            "MemcardB = {dir}/MemoryCardB.{region}.raw\n".format(
                dir=self.get_state_dir(), region=memcard_region
            )
        )

    def dolphin_configure_input(self):
        # devices = self.context.input.get_devices(1, 4)
        input_mapping = {
            "A": "Buttons/A",
            "B": "Buttons/B",
            "X": "Buttons/X",
            "Y": "Buttons/Y",
            "Z": "Buttons/Z",
            "START": "Buttons/Start",
            "STICK_UP": "Main Stick/Up",
            "STICK_DOWN": "Main Stick/Down",
            "STICK_LEFT": "Main Stick/Left",
            "STICK_RIGHT": "Main Stick/Right",
            "C_UP": "C-Stick/Up",  # or z?
            "C_DOWN": "C-Stick/Down",
            "C_LEFT": "C-Stick/Left",
            "C_RIGHT": "C-Stick/Right",
            "L": "Triggers/L",
            "R": "Triggers/R",
            "DPAD_UP": "D-Pad/Up",
            "DPAD_DOWN": "D-Pad/Down",
            "DPAD_LEFT": "D-Pad/Left",
            "DPAD_RIGHT": "D-Pad/Right",
            "L_ANALOG": "Triggers/L-Analog",
            "R_ANALOG": "Triggers/R-Analog",
            # FIXME: ADD MODIFIER?
        }
        temp_dir = self.temp_dir("dolphin")
        input_config_file = os.path.join(
            temp_dir.path, "user", "Config", "GCPadNew.ini"
        )
        f = open(input_config_file, "w")
        for i, port in enumerate(self.ports):
            if not port.device:
                continue
            f.write("[GCPad{num}]\n".format(num=i + 1))
            if port.device.is_keyboard():
                f.write("Device = DInput/0/Keyboard Mouse\n")
            else:
                type_index = int(port.device.id.rsplit("#", 1)[1]) - 1
                f.write(
                    "Device = SDL/{index}/{name}\n".format(
                        index=type_index, name=port.device.sdl_name
                    )
                )
            mapper = DolphinInputMapper(port, input_mapping)
            for key, value in mapper.items():
                if isinstance(key, tuple):
                    for k in key:
                        f.write("{key} = {value}\n".format(key=k, value=value))
                else:
                    f.write("{key} = {value}\n".format(key=key, value=value))


class GameCubeHelper:
    def __init__(self, options):
        self.options = options
