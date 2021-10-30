import io
import os
from configparser import ConfigParser
from typing import Dict, Iterable, List, Optional, Tuple

from fscore.resources import Resources
from fscore.system import System
from fsgamesys.context import fsgs
from fsgamesys.FSGSDirectories import FSGSDirectories
from fspy.decorators import memoize


class InputDeviceNotFoundException(Exception):
    pass


class MissingPlatformSupportException(Exception):
    pass


class InputDeviceInfo(object):
    id = ""
    generic_id = ""
    sdl_name = ""
    name = ""
    buttons = 0
    axes = 0
    hats = 0
    balls = 0
    index = 0

    def get_type(self):
        if self.sdl_name:
            return "TYPE_JOYSTICK"
        else:
            return "TYPE_KEYBOARD"


class LegacyInputDevice(object):
    MissingPlatformSupportException = MissingPlatformSupportException

    def __init__(
        self,
        platform: str,
        name: str,
        sclist: List["LegacyInputDevice"],  # Maybe correct type
        sdl_name: str = "",
        sdl_joystick_id: int = -1,
        version: int = 1,
        buttons: int = 0,
        axes: int = 0,
        hats: int = 0,
        balls: int = 0,
        multiple: bool = True,
    ):
        """
        sclist -- system controller list
        """
        self.type = ""
        self.config: Optional[Dict[str, str]] = None
        self.config_inv: Optional[Dict[str, str]] = None
        self.id = name
        # self._name = name
        if "#" in self.id:
            self.name, _ = self.id.rsplit("#", 1)
        else:
            self.name = self.id
        self.name = self.name.strip()
        self.decorate_name_with_number()

        # print("--------->", self.id)
        # print("------------>", self.name)
        # print("********** InputDevice Constructor", self.name, "ID is",
        #         self.id)

        self.platform = platform
        self.sdl_name = sdl_name
        if not self.sdl_name:
            self.sdl_name = self.id.rsplit("#", 1)[0].strip()
        self.sdl_joystick_id = sdl_joystick_id
        self.index = -1
        self.version = version
        self.buttons = buttons
        self.axes = axes
        self.hats = hats
        self.balls = balls
        for sc in sclist:
            # print("---", name, "---", sc.id, sc.index)
            if name == sc.id:
                self.index = sc.index
                break

        if version == 1:
            method_name = "configure_for_" + platform.lower().replace(
                " ", "_"
            ).replace("-", "_")
            if hasattr(self, method_name):
                getattr(self, method_name)(name, sclist=sclist)
            else:
                print(
                    "{0} does not support platform {1}".format(name, platform)
                )
                raise MissingPlatformSupportException(
                    "No input device support for platform"
                )
        elif version == 2:
            old_name = self.name
            self.configure_version_2(multiple=multiple)
            if self.name != old_name:
                # print("****** name is now", self.name)
                print(self.id, "=>", repr(self.name))

    def decorate_name_with_number(self):
        # print("decorate_name_with_number, ID is", self.id)
        if "#" in self.id:
            _, number_str = self.id.rsplit("#", 1)
        else:
            number_str = "1"
        if number_str != "1":
            self.name = "{0} #{1}".format(self.name, number_str)

    def is_joystick(self):
        return self.get_type() == "TYPE_JOYSTICK"

    def is_keyboard(self):
        return self.get_type() == "TYPE_KEYBOARD"

    def get_type(self):
        if self.type.startswith("joystick"):
            return "TYPE_JOYSTICK"
        elif self.type.startswith("keyboard"):
            return "TYPE_KEYBOARD"
        else:
            raise Exception("unknown input device type " + repr(self.type))

    @classmethod
    def get_builtin_config_for_device_guid(cls, guid: str):
        return Resources("fsgamesys").stream(
            "input/" + guid + ".fs-uae-controller"
        )

    # @classmethod
    # def get_builtin_config_file_for_device_guid(cls, guid):
    #     try:
    #         path = Resources("fsgamesys").path(
    #             "input/" + guid + ".fs-uae-controller")
    #     except LookupError:
    #         return None
    #     return path

    @staticmethod
    @memoize
    def get_config_files() -> Dict[str, str]:
        print("get_config_files")
        configs: Dict[str, str] = {}
        input_stream = Resources("fsgamesys").stream("input/manifest.txt")
        print("opened input manifest")
        for lineBytes in input_stream.read().split(b"\n"):
            line = lineBytes.decode("UTF-8")
            path = line.strip()
            if not path:
                continue
            _, ext = os.path.splitext(path)
            if ext in [".ini", ".conf"]:
                parts = path.split("/")
                file_name = parts[-1]
                name, _ = os.path.splitext(file_name)
                if len(parts) > 1:
                    configs[parts[-2] + "_" + name] = "fsgamesys:input/" + path
                # print(" -", path)
                configs[name] = "fsgamesys:input/" + path

        # FIXME: fix dependency
        controllers_dir = fsgs.amiga.get_controllers_dir()
        print("read configs from controllers_dir at", controllers_dir)
        if os.path.exists(controllers_dir):
            for file_name in os.listdir(controllers_dir):
                if file_name.endswith(".conf"):
                    name, ext = os.path.splitext(file_name)
                    path = os.path.join(controllers_dir, file_name)
                    print(" -", path)
                    configs[name] = path
        keyboards_dir = os.path.join(
            FSGSDirectories.get_data_dir(), "Devs", "Keyboards"
        )
        print("read configs from controllers_dir at", keyboards_dir)
        if os.path.exists(keyboards_dir):
            for file_name in os.listdir(keyboards_dir):
                if file_name.endswith(".ini"):
                    name, ext = os.path.splitext(file_name)
                    path = os.path.join(keyboards_dir, file_name)
                    print(" -", path)
                    configs[name] = path

        # print("input config files:", configs)
        return configs

    def read_config(
        self,
        config_name: str,
        config: Dict[str, str],
        platform: str,
        multiple: bool,
    ) -> None:
        print("read_config", config_name)
        configs = self.get_config_files()
        print(config_name in configs)
        try:
            path = configs[config_name]
        except KeyError:
            # traceback.print_stack()
            print(
                "no config file found for",
                repr(self.sdl_name),
                "=",
                config_name,
            )
            # raise InputDeviceNotFoundException(
            #         "no config found for " + repr(self.sdl_name))
            if platform:
                raise MissingPlatformSupportException(
                    "no config found for " + repr(self.sdl_name)
                )
            else:
                return
        cp = ConfigParser()
        print(path, os.path.exists(path))
        if path.startswith("fsgamesys:"):
            print("reading config from stream", path)
            input_stream_b = Resources("fsgamesys").stream(
                path.split(":", 1)[1]
            )
            input_stream = io.TextIOWrapper(input_stream_b, "UTF-8")
            cp.read_file(input_stream)
        else:
            cp.read(path)
        if cp.has_option("device", "type"):
            self.type = cp.get("device", "type")
        if cp.has_option("device", "name"):
            # print("HAD NAME", self.name, self.sdl_name)
            self.name = cp.get("device", "name")
            self.decorate_name_with_number()
            # print("HAS NAME", self.name, self.sdl_name)
            # try:
            #     dummy, num = self.name.rsplit('#', 1)
            # except ValueError:
            #     self.name = name
            # else:
            #     self.name = "{0} #{1}".format(name, num)
        if cp.has_section(platform):
            section = platform
        elif cp.has_section("default"):
            # print("has default section")
            section = "default"
        else:
            if platform:
                raise MissingPlatformSupportException(
                    "no config found for platform " + repr(platform)
                )
            else:
                return
        # config = {}
        # if section == 'gamepad':
        #
        # for option in cp.options('gamepad'):
        #     value = cp.get('gamepad', option)
        #     print("gamepad", option, value)

        if cp.has_option(section, "include"):
            include_config = cp.get(section, "include")
            include_config = include_config.replace("/", "_")
            self.read_config(include_config, config, platform, multiple)

        # iconfig = {}
        # for key, value in config.items():
        #     iconfig[value] = key

        # for key in cp.options(section):
        #     value = cp.get(section, key)
        self.read_config_2(config, cp.items(section), multiple)

    def read_config_2(
        self,
        config: Dict[str, str],
        items: Iterable[Tuple[str, str]],
        multiple: bool,
    ):
        # for key, value in cp.items(section):
        for key, value in items:
            value = value.strip()
            if value.startswith("("):
                if not multiple:
                    continue
                assert value.endswith(")")
                value = value[1:-1]
            # print(key, "===>", value)
            # print("key, value is", key, value)
            # if value in iconfig:
            try:
                # config[key] = iconfig[value]
                # config[key] = config[value]
                # del config[value]
                # config[config[value]] = value

                # if key in iconfig:
                config[key] = config[value]
                # del iconfig[key]
                # iconfig[config[value]] = key
                # if not config[value] in iconfig:
                #     iconfig[config[value]] = key
                del config[value]
            except KeyError:
                config[key] = value
                # if not value in iconfig:
                #     iconfig[value] = key
                # config_order.append(key)

            # config[option] = cp.get(section, option)

        # if cp.has_section('gamepad'):
        #     for key, value in list(config.items()):
        #         if cp.has_option('gamepad', value):
        #             config[key] = cp.get('gamepad', value)

    def configure_version_2(self, multiple: bool = True):
        self.config = self.configure(self.platform, multiple=multiple)

    def configure(self, platform: str, multiple: bool = True):
        print("CONFIGURE", platform, self.name, self.sdl_name)
        # print("InputDevice.configure")

        name_lower = self.sdl_name.lower()
        name = ""
        for c in name_lower:
            if c in "abcdefghijklmnopqrstuvwxyz0123456789":
                name = name + c
            else:
                if not name.endswith("_"):
                    name += "_"
        name = name.strip("_")
        if System.windows:
            host_platform = "windows"
        elif System.macos:
            host_platform = "macos"
        elif System.linux:
            host_platform = "linux"
        else:
            host_platform = "other"
        config_name = "{0}_{1}_{2}_{3}_{4}_{5}".format(
            name, self.buttons, self.axes, self.hats, self.balls, host_platform
        )

        config: Dict[str, str] = {}
        try:
            self.read_config(self.name, config, platform, multiple)
        except Exception:
            pass
        else:
            return config
        try:
            self.read_config(self.sdl_name, config, platform, multiple)
        except Exception:
            pass
        else:
            return config
        try:
            self.read_config(config_name, config, platform, multiple)
        except Exception:
            pass
        else:
            return config

        config_name = ""
        for c in self.sdl_name.lower():
            if c in "abcdefghijklmnopqrstuvwxyz0123456789":
                config_name += c
            elif len(config_name) == 0 or config_name[-1] != "_":
                config_name += "_"
        if config_name.endswith("_usb"):
            config_name = config_name[:-4]
        while config_name.endswith("_"):
            config_name = config_name[:-1]
        # print("config_name =", config_name, "sdl_name", repr(self.sdl_name))
        self.read_config(config_name, config, platform, multiple)
        return config

    @staticmethod
    def supported_keyboard_input_devices():
        return "", 0

    def get_name(self):
        return self.name

    def get_sdl_joystick_id(self):
        return self.sdl_joystick_id

    def get_config(self):
        if self.config is None:
            raise Exception("InputDevice is not configured")
        return self.config

    def get_config_inverted(self):
        if self.config_inv is not None:
            return self.config_inv
        if self.config is None:
            raise Exception("InputDevice is not configured")
        self.config_inv = {}
        for k, v in self.config.items():
            self.config_inv[v] = k
        return self.config_inv
