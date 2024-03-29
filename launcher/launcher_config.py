import hashlib
import os
import traceback
from configparser import ConfigParser, NoSectionError
from typing import Dict, List, Tuple

from fsbc.paths import Paths
from fsbc.signal import Signal
from fsgamesys.amiga.amiga import Amiga
from fsgamesys.amiga.valueconfigloader import ValueConfigLoader
from fsgamesys.checksumtool import ChecksumTool
from fsgamesys.config.config import Config
from fsgamesys.context import fsgs
from fsgamesys.FSGSDirectories import FSGSDirectories
from fsgamesys.platforms.platform import PlatformHandler
from fspy.decorators import deprecated
from launcher.option import Option

from .launcher_settings import LauncherSettings

cfg = [
    ("amiga_model", "", "checksum", "sync"),
    ("ntsc_mode", "", "checksum", "sync"),
    ("accuracy", "", "checksum", "sync"),
    ("chip_memory", "", "checksum", "sync"),
    ("slow_memory", "", "checksum", "sync"),
    ("fast_memory", "", "checksum", "sync"),
    ("zorro_iii_memory", "", "checksum", "sync"),
    ("bsdsocket_library", "", "checksum", "sync"),
    ("uaegfx_card", "", "checksum", "sync"),
    ("joystick_port_0", ""),
    ("joystick_port_0_mode", "", "checksum", "sync"),
    ("joystick_port_0_autofire", "", "checksum", "sync"),
    ("joystick_port_1", ""),
    ("joystick_port_1_mode", "", "checksum", "sync"),
    ("joystick_port_1_autofire", "", "checksum", "sync"),
    ("joystick_port_2", ""),
    ("joystick_port_2_mode", "", "checksum", "sync"),
    ("joystick_port_2_autofire", "", "checksum", "sync"),
    ("joystick_port_3", ""),
    ("joystick_port_3_mode", "", "checksum", "sync"),
    ("joystick_port_3_autofire", "", "checksum", "sync"),
    ("floppy_drive_count", "", "checksum", "sync"),
    ("cdrom_drive_count", "", "checksum", "sync"),
    # this is not an Amiga device, so no need to checksum / sync
    ("joystick_port_4_mode", "", "custom"),
    ("kickstart_file", ""),
    ("x_kickstart_file", "", "no_save"),
    ("x_kickstart_file_sha1", "", "checksum", "sync", "no_save"),
    ("kickstart_ext_file", ""),
    ("x_kickstart_ext_file", "", "no_save"),
    ("x_kickstart_ext_file_sha1", "", "checksum", "sync", "no_save"),
    (Option.X_WHDLOAD_ARGS, "", "checksum", "sync"),
    (Option.X_WHDLOAD_VERSION, "", "checksum", "sync"),
    # (Option.WHDLOAD_SPLASH_DELAY, "", "checksum", "sync"),
    # (Option.WHDLOAD_QUIT_KEY, "", "checksum", "sync"),
    ("floppy_drive_count", "", "checksum", "sync"),
    ("floppy_drive_speed", "", "checksum", "sync"),
    ("cdrom_drive_count", "", "checksum", "sync"),
    ("dongle_type", "", "checksum", "sync"),
    ("__netplay_game", "", "checksum", "sync"),
    ("__netplay_password", "", "checksum", "sync"),
    ("__netplay_players", "", "checksum", "sync"),
    ("__netplay_port", "", "sync"),
    ("__netplay_addresses", "", "checksum", "sync"),
    ("__netplay_host", ""),
    ("__netplay_ready", ""),
    ("__netplay_state_dir_name", "", "checksum", "sync"),
    ("__version", "FIXME"),
    ("__error", ""),
    ("x_game_uuid", ""),
    ("x_game_xml_path", ""),
    ("title", "", "custom"),
    ("sub_title", "", "custom"),
    ("viewport", "", "custom"),
    ("year", ""),
    ("developer", ""),
    ("publisher", ""),
    ("languages", ""),
    ("players", ""),
    ("protection", ""),
    ("hol_url", ""),
    ("wikipedia_url", ""),
    ("database_url", ""),
    ("lemon_url", ""),
    ("mobygames_url", ""),
    ("amigamemo_url", ""),
    ("whdload_url", ""),
    ("mobygames_url", ""),
    ("thelegacy_url", ""),
    ("homepage_url", ""),
    ("longplay_url", ""),
    ("variant_uuid", ""),
    ("game_uuid", ""),
    ("download_file", ""),
    ("download_page", ""),
    ("download_terms", ""),
    ("download_notice", ""),
    ("x_missing_files", ""),
    ("x_game_notice", ""),
    ("x_variant_notice", ""),
    ("x_variant_warning", ""),
    ("x_variant_error", ""),
    ("x_joy_emu_conflict", ""),
    ("screen1_sha1", ""),
    ("screen2_sha1", ""),
    ("screen3_sha1", ""),
    ("screen4_sha1", ""),
    ("screen5_sha1", ""),
    ("front_sha1", ""),
    ("title_sha1", ""),
    ("mouse_integration", "", "checksum", "sync"),
    ("cdrom_drive_0_delay", "", "checksum", "sync"),
    ("cpu", "", "checksum", "sync"),
    ("graphics_card", "", "checksum", "sync"),
    ("graphics_memory", "", "checksum", "sync"),
    ("accelerator", "", "checksum", "sync"),
    ("accelerator_memory", "", "checksum", "sync"),
    ("blizzard_scsi_kit", "", "checksum", "sync"),
    ("motherboard_ram", "", "checksum", "sync"),
    ("sound_card", "", "checksum", "sync"),
    ("jit_compiler", "", "checksum", "sync"),
    ("__database", ""),
    ("platform", ""),
    ("save_disk", "", "checksum", "sync"),
    ("network_card", "", "checksum", "sync"),
    ("freezer_cartridge", "", "checksum", "sync"),
    (Option.A7800_A78_HEADER, "", "checksum", "sync"),
    (Option.A7800_MODEL, "", "checksum", "sync"),
    (Option.A7800_PORT_1_TYPE, "", "checksum", "sync"),
    (Option.A7800_PORT_2_TYPE, "", "checksum", "sync"),
    (Option.CPC_MODEL, "", "checksum", "sync"),
    (Option.COMMAND, "", "checksum", "sync"),
    (Option.NES_MODEL, "", "checksum", "sync"),
    (Option.C64_MODEL, "", "checksum", "sync"),
    (Option.CARTRIDGE_SLOT, "", "checksum", "sync"),
    (Option.FILE_LIST, "", "custom", "sync"),
    (Option.FLOPPY_DRIVE_VOLUME_EMPTY, "", "sync"),
    (Option.GAME_NAME, ""),
    ("mame_rom_set", "", "custom", "checksum", "sync"),
    (Option.NEOGEO_MODEL, "", "checksum", "sync"),
    (Option.NES_INES_HEADER, "", "checksum", "sync"),
    (Option.NES_MODEL, "", "checksum", "sync"),
    (Option.NES_PORT_1_TYPE, "", "checksum", "sync"),
    (Option.NES_PORT_2_TYPE, "", "checksum", "sync"),
    (Option.NES_PORT_3_TYPE, "", "checksum", "sync"),
    (Option.NES_PORT_4_TYPE, "", "checksum", "sync"),
    (Option.SMD_EMULATOR, "", "checksum", "sync"),
    (Option.SMD_MODEL, "", "checksum", "sync"),
    (Option.SMD_PORT_1_TYPE, "", "checksum", "sync"),
    (Option.SMD_PORT_2_TYPE, "", "checksum", "sync"),
    (Option.SNES_PORT_1_TYPE, "", "checksum", "sync"),
    (Option.SNES_PORT_2_TYPE, "", "checksum", "sync"),
    (Option.ST_MODEL, "", "checksum", "sync"),
    ("refresh_rate", "", "custom", "checksum", "sync"),
    (Option.TAPE_DRIVE_0, "", "checksum", "sync"),
    ("tape_image_0", "", "checksum", "sync"),
    (Option.VARIANT_NAME, ""),
    (Option.ZXS_MODEL, "", "checksum", "sync"),
]

for _i in range(Amiga.MAX_FLOPPY_DRIVES):
    cfg.append(("floppy_drive_{0}".format(_i), ""))
    cfg.append(
        (
            "x_floppy_drive_{0}_sha1".format(_i),
            "",
            "checksum",
            "sync",
            "no_save",
        )
    )
for _i in range(Amiga.MAX_FLOPPY_IMAGES):
    cfg.append(("floppy_image_{0}".format(_i), ""))
    cfg.append(
        (
            "x_floppy_image_{0}_sha1".format(_i),
            "",
            "checksum",
            "sync",
            "no_save",
        )
    )
for _i in range(Amiga.MAX_CDROM_DRIVES):
    cfg.append(("cdrom_drive_{0}".format(_i), ""))
    cfg.append(
        (
            "x_cdrom_drive_{0}_sha1".format(_i),
            "",
            "checksum",
            "sync",
            "no_save",
        )
    )
for _i in range(Amiga.MAX_CDROM_IMAGES):
    cfg.append(("cdrom_image_{0}".format(_i), ""))
    cfg.append(
        (
            "x_cdrom_image_{0}_sha1".format(_i),
            "",
            "checksum",
            "sync",
            "no_save",
        )
    )
for _i in range(Amiga.MAX_HARD_DRIVES):
    cfg.append(("hard_drive_{0}".format(_i), ""))
    cfg.append(
        ("hard_drive_{0}_label".format(_i), "", "checksum", "sync", "custom")
    )
    cfg.append(
        (
            "hard_drive_{0}_priority".format(_i),
            "",
            "checksum",
            "sync",
            "custom",
        )
    )
    cfg.append(
        ("x_hard_drive_{0}_sha1".format(_i), "", "checksum", "sync", "no_save")
    )

default_config = {}
for c in cfg:
    default_config[c[0]] = c[1]

checksum_keys = [x[0] for x in cfg if "checksum" in x]


class LauncherConfig(object):
    config_keys = [x[0] for x in cfg]

    default_config = default_config
    checksum_keys = checksum_keys
    key_order = [x[0] for x in cfg]
    sync_keys_list = [x[0] for x in cfg if "sync" in x]
    sync_keys_set = set(sync_keys_list)
    no_custom_config = [x[0] for x in cfg if "custom" not in x]

    no_custom_config.append("__changed")
    no_custom_config.append("__ready")
    no_custom_config.append("__config_name")
    # no_custom_config.append("__database")
    # no_custom_config.append("x_whdload_icon")
    # no_custom_config.append("platform")

    no_save_keys_set = set([x[0] for x in cfg if "no_save" in x])

    reset_values = {}
    for i in range(Amiga.MAX_FLOPPY_DRIVES):
        reset_values["floppy_drive_{0}".format(i)] = (
            "x_floppy_drive_{0}_sha1".format(i),
            "",
        )
    for i in range(Amiga.MAX_FLOPPY_IMAGES):
        reset_values["floppy_image_{0}".format(i)] = (
            "x_floppy_image_{0}_sha1".format(i),
            "",
        )
    for i in range(Amiga.MAX_CDROM_DRIVES):
        reset_values["cdrom_drive_{0}".format(i)] = (
            "x_cdrom_drive_{0}_sha1".format(i),
            "",
        )
    for i in range(Amiga.MAX_CDROM_IMAGES):
        reset_values["cdrom_image_{0}".format(i)] = (
            "x_cdrom_image_{0}_sha1".format(i),
            "",
        )
    for i in range(Amiga.MAX_HARD_DRIVES):
        reset_values["hard_drive_{0}".format(i)] = (
            "x_hard_drive_{0}_sha1".format(i),
            "",
        )
    reset_values["x_kickstart_file"] = ("x_kickstart_file_sha1", "")
    reset_values["x_kickstart_ext_file"] = ("x_kickstart_ext_file_sha1", "")

    # config = default_config.copy()
    # config_listeners = []

    @classmethod
    @deprecated
    def keys(cls):
        return fsgs.config.values.keys()

    @classmethod
    @deprecated
    def copy(cls):
        return fsgs.config.copy()

    @classmethod
    @deprecated
    def get(cls, key, default=""):
        return fsgs.config.get(key, default)

    @classmethod
    @deprecated
    def add_listener(cls, listener):
        # deprecated
        Signal("fsgs:config").connect(getattr(listener, "on_config"))

    @classmethod
    @deprecated
    def remove_listener(cls, listener):
        # deprecated
        Signal("fsgs:config").disconnect(getattr(listener, "on_config"))

    @classmethod
    @deprecated
    def set(cls, key: str, value: str):
        fsgs.config.set(key, value)

    @classmethod
    @deprecated
    def set_multiple(cls, items: List[Tuple[str, str]]):
        fsgs.config.set_multiple(items)

    @classmethod
    @deprecated
    def update_from_config_dict(cls, config_dict: Dict[str, str]):
        # changes = []
        # for key, value in config_dict.items():
        #     if key in fsgs.config.values:
        #         if fsgs.config.values[key] != value:
        #             changes.append((key, value))
        #     else:
        #         changes.append((key, value))
        # cls.set_multiple(changes)
        LauncherConfig.update_config_from_config_dict(fsgs.config, config_dict)

    @staticmethod
    def update_config_from_config_dict(
        config: Config, config_dict: Dict[str, str]
    ):
        changes: List[Tuple[str, str]] = []
        for key, value in config_dict.items():
            if key in fsgs.config.values:
                if fsgs.config.values[key] != value:
                    changes.append((key, value))
            else:
                changes.append((key, value))
        config.set_multiple(changes)

    @classmethod
    @deprecated
    def sync_items(cls):
        for key, value in fsgs.config.values.items():
            if key in cls.sync_keys_set:
                yield key, value

    @classmethod
    @deprecated
    def checksum(cls):
        return cls.checksum_config(fsgs.config.copy())

    @staticmethod
    def checksum_config(config):
        s = hashlib.sha1()
        for key in checksum_keys:
            value = config[key]
            s.update(str(value).encode("UTF-8"))
        return s.hexdigest()

    @staticmethod
    def update_kickstart_in_config_dict(config_dict: Dict[str, str]):
        print("update_kickstart_in_config")
        model = config_dict.setdefault(
            "amiga_model", default_config["amiga_model"]
        )

        kickstart_file = config_dict.setdefault("kickstart_file", "")
        if kickstart_file:
            config_dict["x_kickstart_file"] = config_dict["kickstart_file"]
            if kickstart_file == "internal":
                config_dict["x_kickstart_file_sha1"] = Amiga.INTERNAL_ROM_SHA1
            else:
                # FIXME: set checksum
                pass
        else:
            checksums = Amiga.get_model_config(model)["kickstarts"]
            for checksum in checksums:
                path = fsgs.file.find_by_sha1(checksum)
                if path:
                    config_dict["x_kickstart_file"] = path
                    config_dict["x_kickstart_file_sha1"] = checksum
                    break
            else:
                print("WARNING: no suitable kickstart file found")
                config_dict["x_kickstart_file"] = ""
                config_dict["x_kickstart_file_sha1"] = Amiga.INTERNAL_ROM_SHA1

        if config_dict.setdefault("kickstart_ext_file", ""):
            config_dict["x_kickstart_ext_file"] = config_dict[
                "kickstart_ext_file"
            ]
            # FIXME: set checksum
        else:
            checksums = Amiga.get_model_config(model)["ext_roms"]
            if len(checksums) == 0:
                config_dict["x_kickstart_ext_file"] = ""
                config_dict["x_kickstart_ext_file_sha1"] = ""
            else:
                for checksum in checksums:
                    path = fsgs.file.find_by_sha1(checksum)
                    if path:
                        config_dict["x_kickstart_ext_file"] = path
                        config_dict["x_kickstart_ext_file_sha1"] = checksum
                        break
                else:
                    # print("WARNING: no suitable kickstart ext file found")
                    config_dict["x_kickstart_ext_file"] = ""
                    config_dict["x_kickstart_ext_file_sha1"] = ""
                    # Warnings.set("hardware", "kickstart_ext",
                    #              "No suitable extended kickstart found")
                    # FIXME: set sha1 and name x_options also

    @classmethod
    def update_kickstart(cls, config: Config):
        config_dict = config.values.copy()
        # cls.set_kickstart_from_model()
        cls.update_kickstart_in_config_dict(config_dict)
        cls.update_config_from_config_dict(config, config_dict)

    @classmethod
    @deprecated
    def set_kickstart_from_model(cls):
        print("set_kickstart_from_model")
        config_dict = fsgs.config.values.copy()
        cls.update_kickstart_in_config_dict(config_dict)
        LauncherConfig.update_config_from_config_dict(fsgs.config, config_dict)

    @classmethod
    @deprecated
    def load_default_config(cls, platform=""):
        print("load_default_config platform =", platform)
        if platform:
            cls.load({Option.PLATFORM: platform})
        else:
            cls.load({})
        LauncherSettings.set(Option.CONFIG_NAME, "Unnamed Configuration")
        LauncherSettings.set("config_path", "")

    @classmethod
    @deprecated
    def load(cls, config):
        update_config = {}
        for key, value in default_config.items():
            update_config[key] = value
        for key in list(fsgs.config.values.keys()):
            if key not in default_config:
                # We need to broadcast changed for all config keys, also
                # the ones this class does not know about
                if key.startswith("__implicit_"):
                    # Unless it is an implicit config key, in which case
                    # it should be properly updated by another component, and
                    # we don't want to have the options flip-flop too much.
                    pass
                elif key in ["__changed"]:
                    # We handle this key explicitly, below.
                    pass
                else:
                    update_config[key] = ""

        for key, value in config.items():
            # if this is a settings key, change settings instead
            if key in LauncherSettings.initialize_from_config:
                LauncherSettings.set(key, value)
            else:
                update_config[key] = value

        cls.update_kickstart_in_config_dict(update_config)
        cls.fix_loaded_config(update_config)
        # print("about to set", update_config)
        cls.set_multiple(update_config.items())
        # Settings.set("config_changed", "0")
        if "__changed" in update_config:
            # We specifically loaded __changed, probably in fix_loaded_config.
            print("__changed was explicitly set:", update_config["__changed"])
        else:
            # Mark config as unchanged (i.e. does not need to be saved).
            cls.set("__changed", "0")

            # cls.update_kickstart()

    @staticmethod
    def fix_joystick_ports(config):
        # from .Settings import Settings

        print("---", config["joystick_port_0"])
        print("---", config["joystick_port_1"])

        from .devicemanager import DeviceManager

        available = DeviceManager.get_joystick_names()
        available.extend(["none", "mouse", "keyboard"])
        available_lower = [x.lower() for x in available]

        device_ids = DeviceManager.get_joystick_ids()
        device_ids.extend(["none", "mouse", "keyboard"])

        # remove devices from available list if specified and found
        try:
            index = available_lower.index(config["joystick_port_1"].lower())
        except ValueError:
            pass
        else:
            del available[index]
            del available_lower[index]
        try:
            index = available_lower.index(config["joystick_port_0"].lower())
        except ValueError:
            pass
        else:
            del available[index]
            del available_lower[index]

        # if config in
        # print("--------------------------------------------")
        if config["joystick_port_1_mode"] in ["joystick", "cd32 gamepad"]:
            if not config["joystick_port_1"]:
                want = LauncherSettings.get("primary_joystick").lower()
                # print("want", want)
                try:
                    index = available_lower.index(want)
                except ValueError:
                    index = -1
                print("available", available_lower)
                print("want", repr(want), "index", index)
                if index == -1:
                    index = len(available) - 1
                if index >= 0:
                    config["joystick_port_1"] = device_ids[index]
                    del available[index]
                    del available_lower[index]
                    del device_ids[index]
        elif config["joystick_port_1_mode"] in ["mouse"]:
            if not config["joystick_port_1"]:
                config["joystick_port_1"] = "mouse"
        elif config["joystick_port_1_mode"] in ["nothing"]:
            if not config["joystick_port_1"]:
                config["joystick_port_1"] = "none"

        if config["joystick_port_0_mode"] in ["joystick", "cd32 gamepad"]:
            if not config["joystick_port_0"]:
                want = LauncherSettings.get("secondary_joystick").lower()
                try:
                    index = available_lower.index(want)
                except ValueError:
                    index = -1
                # print("want", want, "index", index)
                if index == -1:
                    index = len(available) - 1
                if index >= 0:
                    config["joystick_port_0"] = device_ids[index]
                    del available[index]
                    del available_lower[index]
                    del device_ids[index]
        elif config["joystick_port_0_mode"] in ["mouse"]:
            if not config["joystick_port_0"]:
                config["joystick_port_0"] = "mouse"
        elif config["joystick_port_0_mode"] in ["nothing"]:
            if not config["joystick_port_0"]:
                config["joystick_port_0"] = "none"

    @classmethod
    @deprecated
    def load_file(cls, path):
        try:
            return cls._load_file(path, "")
        except Exception:
            # FIXME: errors should be logged / displayed
            cls.load_default_config()
            traceback.print_exc()
        return False

    @classmethod
    @deprecated
    def load_data(cls, data):
        print("Config.load_data")
        try:
            cls._load_file("", data)
        except Exception:
            # FIXME: errors should be logged / displayed
            cls.load_default_config()
            traceback.print_exc()

    @classmethod
    @deprecated
    def create_fs_name(cls, name):
        name = name.replace(":", " - ")
        name = name.replace("*", "-")
        name = name.replace("?", "")
        name = name.replace("/", "-")
        name = name.replace("\\", "-")
        name = name.replace('"', "'")
        for i in range(3):
            name = name.replace("  ", " ")
        while name.endswith("."):
            name = name[:-1]
        name = name.strip()
        return name

    @classmethod
    @deprecated
    def _load_file(cls, path, data):
        if data:
            print("loading config from data")
        else:
            print("loading config from " + repr(path))
            if not os.path.exists(path):
                print("config file does not exist")
        if data:
            raise Exception("_load_file (data) not implemented")
        else:
            cp = ConfigParser(interpolation=None, strict=False)
            try:
                with open(path, "r", encoding="UTF-8") as f:
                    cp.read_file(f)
            except Exception as e:
                print(repr(e))
                return False
            config = {}
            try:
                keys = cp.options("config")
            except NoSectionError:
                keys = []
            for key in keys:
                config[key] = cp.get("config", key)
            try:
                keys = cp.options("fs-uae")
            except NoSectionError:
                keys = []
            for key in keys:
                config[key] = cp.get("fs-uae", key)

        LauncherSettings.set("config_path", path)

        print("__changed before load:", cls.get("__changed"))
        cls.load(config)
        print("__changed after load:", cls.get("__changed"))
        # Changed may have been set by fix_loaded_config
        changed = cls.get("__changed", "0")

        config_name = config.get("__config_name", "")
        if config_name:
            config_name = cls.create_fs_name(config_name)
        else:
            config_name, ext = os.path.splitext(os.path.basename(path))

        LauncherSettings.set(Option.CONFIG_NAME, config_name)
        cls.set("__changed", changed)
        return True

    @classmethod
    @deprecated
    def load_values(cls, values, uuid=""):
        # print("loading config values", values)
        platform_id = values.get("platform", "").lower()

        if platform_id in ["amiga", "cdtv", "cd32"]:
            value_config_loader = ValueConfigLoader(uuid=uuid)
            value_config_loader.load_values(values)
            config = value_config_loader.get_config()
            cls.load(config)
            values["__config_name"] = config.get("__config_name")
        else:
            print("Warning: Non-Amiga game loaded")
            platform_handler = PlatformHandler.create(platform_id)
            loader = platform_handler.get_loader(fsgs)
            fsgs.config.load(loader.load_values(values))
        cls.post_load_values(values)

    @staticmethod
    def post_load_values(values):
        print("POST_LOAD_VALUES")
        if values.get("__config_name", ""):
            print("__config_name was set")
            config_name = values.get("__config_name", "")
        else:
            config_name = "{0} ({1})".format(
                values.get("game_name"), values.get("variant_name")
            )
        LauncherSettings.set("config_path", "")
        if config_name:
            config_name = cls.create_fs_name(config_name)
        LauncherSettings.set(Option.CONFIG_NAME, config_name)
        cls.set("__changed", "0")

    @staticmethod
    def is_implicit_option(key: str) -> bool:
        return key.startswith("__implicit_")

    @staticmethod
    def is_custom_uae_option(key: str) -> bool:
        return key.startswith("uae_")

    @classmethod
    def is_custom_option(cls, key: str) -> bool:
        return key not in cls.config_keys

    @classmethod
    def is_config_only_option(cls, key: str) -> bool:
        if key in LauncherSettings.default_settings:
            # This key is specifically white-listed as a settings key
            return False
        if cls.is_custom_uae_option(key):
            return True
        if not cls.is_custom_option(key):
            return True
        return False

    @staticmethod
    def fix_loaded_config(config):
        print("[CONFIG] Fix loaded config")
        # cls.fix_joystick_ports(config)

        # FIXME: parent
        checksum_tool = ChecksumTool(None)

        def fix_file_checksum(sha1_key, key, base_dir, is_rom=False):
            path = config.get(key, "")
            # hack to synchronize URLs
            # print(repr(path))
            if path.startswith("http://") or path.startswith("https://"):
                sha1 = path
                config[sha1_key] = sha1
                return
            path = Paths.expand_path(path)
            sha1 = config.get(sha1_key, "")
            if not path:
                return
            if sha1:
                # assuming sha1 is correct
                return
            if not os.path.exists(path):
                print(repr(path), "does not exist")
                path = os.path.join(base_dir, path)
                if not os.path.exists(path):
                    print(repr(path), "does not exist")
                    return
            if os.path.isdir(path):
                # could set a fake checksum here or something, to indicate
                # that it isn't supposed to be set..
                return
            print("checksumming", repr(path))
            size = os.path.getsize(path)
            if size > 64 * 1024 * 1024:
                # not checksumming large files right now
                print("not checksumming large file")
                return

            if is_rom:
                sha1 = checksum_tool.checksum_rom(path)
            else:
                sha1 = checksum_tool.checksum(path)
            config[sha1_key] = sha1

        for i in range(Amiga.MAX_FLOPPY_DRIVES):
            fix_file_checksum(
                "x_floppy_drive_{0}_sha1".format(i),
                "floppy_drive_{0}".format(i),
                FSGSDirectories.get_floppies_dir(),
            )
        for i in range(Amiga.MAX_FLOPPY_IMAGES):
            fix_file_checksum(
                "x_floppy_image_{0}_sha1".format(i),
                "floppy_image_{0}".format(i),
                FSGSDirectories.get_floppies_dir(),
            )
        for i in range(Amiga.MAX_CDROM_DRIVES):
            fix_file_checksum(
                "x_cdrom_drive_{0}_sha1".format(i),
                "cdrom_drive_{0}".format(i),
                FSGSDirectories.get_cdroms_dir(),
            )
        for i in range(Amiga.MAX_CDROM_IMAGES):
            fix_file_checksum(
                "x_cdrom_image_{0}_sha1".format(i),
                "cdrom_image_{0}".format(i),
                FSGSDirectories.get_cdroms_dir(),
            )
        for i in range(Amiga.MAX_HARD_DRIVES):
            fix_file_checksum(
                "x_hard_drive_{0}_sha1".format(i),
                "hard_drive_{0}".format(i),
                FSGSDirectories.get_hard_drives_dir(),
            )

        # FIXME: need to handle checksums for Cloanto here
        fix_file_checksum(
            "x_kickstart_file_sha1",
            "x_kickstart_file",
            FSGSDirectories.get_kickstarts_dir(),
            is_rom=True,
        )
        fix_file_checksum(
            "x_kickstart_ext_file_sha1",
            "x_kickstart_ext_file",
            FSGSDirectories.get_kickstarts_dir(),
            is_rom=True,
        )

        # Convert uaegfx_card to new graphics_card option
        uae_gfx_card = config.get(Option.UAEGFX_CARD, "")
        if uae_gfx_card:
            if uae_gfx_card == "1":
                if not config.get(Option.GRAPHICS_CARD, ""):
                    config[Option.GRAPHICS_CARD] = "uaegfx"
            del config[Option.UAEGFX_CARD]
            # FIXME: Set changed!
            config["__changed"] = "1"
