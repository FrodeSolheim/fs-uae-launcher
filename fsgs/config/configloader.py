import os
from configparser import ConfigParser, NoSectionError

from fsgs.amiga.valueconfigloader import ValueConfigLoader
from fsgs.options.constants2 import (
    CHANGED__,
    CONFIG_PATH__,
    DATABASE_NAME__,
    GAME_UUID__,
    PARENT_UUID,
    VARIANT_UUID__,
)
from fsgs.platform import PlatformHandler


class ConfigLoader:
    def __init__(self, config):
        self._config = config

    def load_config_file(self, config_path):
        print("-" * 79)
        print("ConfigLoader.load_config_file")
        print(config_path)
        if not os.path.exists(config_path):
            print("config file does not exist")

        cp = ConfigParser(interpolation=None, strict=False)
        try:
            with open(config_path, "r", encoding="UTF-8") as f:
                cp.read_file(f)
        except Exception as e:
            print(repr(e))
            return False
        new_config = {}
        try:
            keys = cp.options("config")
        except NoSectionError:
            keys = []
        for key in keys:
            new_config[key] = cp.get("config", key)
        try:
            keys = cp.options("fs-uae")
        except NoSectionError:
            keys = []
        for key in keys:
            new_config[key] = cp.get("fs-uae", key)
        self.load_config_values(new_config, config_path=config_path)

        # LauncherSettings.set("config_path", path)
        # print("__changed before load:", cls.get("__changed"))
        # cls.load(config)
        # print("__changed after load:", cls.get("__changed"))
        # # Changed may have been set by fix_loaded_config
        # changed = cls.get("__changed", "0")

        # config_name = config.get("__config_name", "")
        # if config_name:
        #     config_name = cls.create_fs_name(config_name)
        # else:
        #     config_name, ext = os.path.splitext(os.path.basename(path))

        # LauncherSettings.set(Option.CONFIG_NAME, config_name)
        # cls.set("__changed", changed)
        # return True

    def load_config_values(self, new_config, *, config_path):
        # self._config.clear()
        # self._config.set(new_config.items())
        new_config[CONFIG_PATH__] = config_path
        self._config.clear_and_set(new_config.items())

    def load_database_values(
        self, values, *, database_name, game_uuid, variant_uuid
    ):
        print("-" * 79)
        print("ConfigLoader.load_database_values")
        # LauncherConfig.set("__changed", "0")
        # LauncherConfig.set("__database", database_name)

        # self.load_values(values, uuid=variant_uuid)

        platform_id = values.get("platform", "").lower()
        if platform_id in ["", "amiga", "cdtv", "cd32"]:
            value_config_loader = ValueConfigLoader(uuid=variant_uuid)
            value_config_loader.load_values(values)
            new_config = value_config_loader.get_config()
        else:
            platform_handler = PlatformHandler.create(platform_id)
            # FIXME:
            fsgs = None
            loader = platform_handler.get_loader(fsgs)
            new_config = loader.load_values(values)

        # self._config.set(__CHANGED, "0")
        # self._config.set(__DATABASE_NAME, database_name)
        # self._config.set_multiple()
        new_config[CHANGED__] = 0
        new_config[DATABASE_NAME__] = database_name
        new_config[GAME_UUID__] = game_uuid
        # VariantBrowser expects parent_uuid to be set
        new_config[PARENT_UUID] = game_uuid
        new_config[VARIANT_UUID__] = variant_uuid
        from pprint import pprint

        pprint(new_config)

        # self._config.clear()
        self._config.clear_and_set(new_config.items())

        # values["__config_name"] = config.get("__config_name")

        # self.load(config)

    # def load(self, values):
    #     self._config.clear()
    #     for key, value in list(values.items()):
    #         self._config.set(key, value)

    # def load_values(self, values, uuid=""):
    #     # print("loading config values", values)
    #     platform_id = values.get("platform", "").lower()
    #     if platform_id in ["", "amiga", "cdtv", "cd32"]:
    #         value_config_loader = ValueConfigLoader(uuid=uuid)
    #         value_config_loader.load_values(values)
    #         config = value_config_loader.get_config()
    #     else:
    #         platform_handler = PlatformHandler.create(platform_id)
    #         # FIXME:
    #         fsgs = None
    #         loader = platform_handler.get_loader(fsgs)
    #         config = loader.load_values(values)

    #     self.load(config)
    #     values["__config_name"] = config.get("__config_name")

    #     self.post_load_values(values)

    # def post_load_values(self, values):
    #     print("POST_LOAD_VALUES")
    #     if values.get("__config_name", ""):
    #         print("__config_name was set")
    #         config_name = values.get("__config_name", "")
    #     else:
    #         config_name = "{0} ({1})".format(
    #             values.get("game_name"), values.get("variant_name")
    #         )
    #     LauncherSettings.set("config_path", "")
    #     if config_name:
    #         config_name = cls.create_fs_name(config_name)
    #     LauncherSettings.set(Option.CONFIG_NAME, config_name)
    #     cls.set("__changed", "0")
