import os
import io
import time
import hashlib
import datetime
from launcher.launcher_config import LauncherConfig
from launcher.configuration_scanner import ConfigurationScanner
from launcher.i18n import gettext
from launcher.launcher_settings import LauncherSettings
from launcher.ui.IconButton import IconButton
from fsgs.Database import Database
from fsgs.FSGSDirectories import FSGSDirectories
from fsgs.FileDatabase import FileDatabase
from fsgs.context import fsgs


class SaveButton(IconButton):

    def __init__(self, parent):
        super().__init__(parent, "save_button.png")
        self.set_tooltip(gettext("Save Config"))
        LauncherConfig.add_listener(self)
        self.on_config("__changed", LauncherConfig.get("__changed"))

    def on_destroy(self):
        LauncherConfig.remove_listener(self)

    def on_config(self, key, value):
        if key == "__changed":
            self.enable(value == "1")

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
        database = Database.get_instance()

        name = LauncherSettings.get("config_name").strip()
        if not name:
            print("no config_name")
            # FIXME: notify user
            return

        file_name = name + ".fs-uae"
        path = os.path.join(
            FSGSDirectories.get_configurations_dir(), file_name)
        with io.open(path, "w", encoding="UTF-8") as f:
            f.write("# FS-UAE configuration saved by FS-UAE Launcher\n")
            f.write("# Last saved: {0}\n".format(
                    datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")))
            f.write("\n[fs-uae]\n")
            keys = sorted(fsgs.config.values.keys())
            for key in keys:
                value = LauncherConfig.get(key)
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
            path=path, name=scanner.create_configuration_name(name))
        database.update_game_search_terms(
            game_id, scanner.create_search_terms(name))

        database.commit()
        file_database.commit()

        LauncherSettings.set("__config_refresh", str(time.time()))
        # Settings.set("config_changed", "0")
        LauncherConfig.set("__changed", "0")
