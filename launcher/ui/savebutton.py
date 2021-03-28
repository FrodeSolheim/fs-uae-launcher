import datetime
import hashlib
import io
import os
import time

from fsgamesys.context import fsgs
from fsgamesys.Database import Database
from fsgamesys.filedatabase import FileDatabase
from fsgamesys.FSGSDirectories import FSGSDirectories
from fsgamesys.platforms import PLATFORM_ID_SPECTRUM
from launcher.configuration_scanner import ConfigurationScanner
from launcher.context import get_config
from launcher.i18n import gettext
from launcher.launcher_config import LauncherConfig
from launcher.launcher_settings import LauncherSettings
from launcher.ui.IconButton import IconButton


class SaveButton(IconButton):
    def __init__(self, parent):
        super().__init__(parent, "save_button.png")
        self.set_tooltip(gettext("Save Config"))
        config = get_config(self)
        config.add_listener(self)
        self.on_config("__changed", config.get("__changed"))

    def on_destroy(self):
        config = get_config(self)
        config.remove_listener(self)
        super().on_destroy()

    def on_config(self, key, value):
        if key == "__changed":
            self.set_enabled(value == "1")

    def on_activate(self):
        print("SaveButton.on_activate")
        # try:
        self.save_config()
        # except Exception:
        #     # FIXME: notify user
        #     pass

    @staticmethod
    def save_config():
        print("SaveButton.save_config")
        config = get_config(self)
        database = Database.get_instance()

        name = LauncherSettings.get("config_name").strip()
        if not name:
            print("no config_name")
            # FIXME: notify user
            return

        file_name = name + get_extension_for_config(config)
        path = os.path.join(
            FSGSDirectories.get_configurations_dir(), file_name
        )
        with io.open(path, "w", encoding="UTF-8") as f:
            f.write("# FS-UAE configuration saved by FS-UAE Launcher\n")
            f.write(
                "# Last saved: {0}\n".format(
                    datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")
                )
            )
            f.write("\n[fs-uae]\n")
            keys = sorted(fsgs.config.values.keys())
            for key in keys:
                value = config.get(key)
                if key.startswith("__"):
                    continue
                if key in LauncherConfig.no_save_keys_set:
                    continue
                # elif key == "joystick_port_2_mode" and value == "nothing":
                #     continue
                # elif key == "joystick_port_3_mode" and value == "nothing":
                #     continue
                if value == LauncherConfig.default_config.get(key, ""):
                    continue
                if value:
                    f.write("{0} = {1}\n".format(key, value))

        # scanner = ConfigurationScanner()
        # search = ConfigurationScanner.create_configuration_search(name)
        # name = scanner.create_configuration_name(name)
        # print("adding", path)
        # # deleting the path from the database first in case it already exists
        # database.delete_configuration(path=path)
        # database.delete_file(path=path)
        # database.add_file(path=path)
        # database.add_configuration(
        #     path=path, uuid="", name=name, scan=0, search=search)

        file_database = FileDatabase.get_instance()
        scanner = ConfigurationScanner()
        print("[save config] adding config", path)
        file_database.delete_file(path=path)
        with open(path, "rb") as f:
            sha1 = hashlib.sha1(f.read()).hexdigest()
        file_database.add_file(path=path, sha1=sha1)

        game_id = database.add_configuration(
            path=path, name=scanner.create_configuration_name(name)
        )
        database.update_game_search_terms(
            game_id, scanner.create_search_terms(name)
        )

        database.commit()
        file_database.commit()

        LauncherSettings.set("__config_refresh", str(time.time()))
        # Settings.set("config_changed", "0")
        LauncherConfig.set("__changed", "0")


def get_extension_for_config(config):
    platform_id = config.get("platform")
    if not platform_id:
        platform_id = Product.default_platform
    if platform_id == PLATFORM_ID_SPECTRUM:
        return ".fs-fuse"
    else:
        return ".fs-uae"
