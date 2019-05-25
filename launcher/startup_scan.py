import hashlib
import os

from fsbc.paths import Paths
from fsgs.Database import Database
from fsgs.FSGSDirectories import FSGSDirectories
from fsgs.filedatabase import FileDatabase
from fsgs.amiga.amiga import Amiga
from fsgs.amiga.rommanager import ROMManager
from fsgs.context import fsgs
from launcher.configuration_scanner import ConfigurationScanner
from launcher.launcher_settings import LauncherSettings


class StartupScan:
    _config_scanned = False
    _kickstart_scanned = False

    @classmethod
    def config_startup_scan(cls):
        if cls._config_scanned:
            return
        cls._config_scanned = True

        configs_dir = FSGSDirectories.get_configurations_dir()
        print("config_startup_scan", configs_dir)
        print(LauncherSettings.settings)

        settings_mtime = LauncherSettings.get("configurations_dir_mtime")
        dir_mtime = cls.get_dir_mtime_str(configs_dir)
        if settings_mtime == dir_mtime + "+" + str(Database.VERSION):
            print("... mtime not changed", settings_mtime, dir_mtime)
            return

        database = Database.get_instance()
        file_database = FileDatabase.get_instance()

        print("... database.find_local_configurations")
        local_configs = Database.get_instance().find_local_configurations()
        print("... walk configs_dir")
        for dir_path, dir_names, file_names in os.walk(configs_dir):
            for file_name in file_names:
                if not file_name.endswith(".fs-uae"):
                    continue
                path = Paths.join(dir_path, file_name)
                if path in local_configs:
                    local_configs[path] = None
                    # already exists in database
                    continue
                name, ext = os.path.splitext(file_name)
                # search = ConfigurationScanner.create_configuration_search(
                # name)
                scanner = ConfigurationScanner()
                print("[startup] adding config", path)
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

        for path, config_id in local_configs.items():
            if config_id is not None:
                print("[startup] removing configuration", path)
                database.delete_game(id=config_id)
                file_database.delete_file(path=path)
        print("... commit")
        database.commit()

        LauncherSettings.set(
            "configurations_dir_mtime",
            cls.get_dir_mtime_str(configs_dir) + "+" + str(Database.VERSION),
        )

    @classmethod
    def kickstart_startup_scan(cls):
        if cls._kickstart_scanned:
            return
        cls._kickstart_scanned = True

        print("kickstart_startup_scan")
        kickstarts_dir = FSGSDirectories.get_kickstarts_dir()
        if LauncherSettings.get(
            "kickstarts_dir_mtime"
        ) == cls.get_dir_mtime_str(kickstarts_dir):
            print("... mtime not changed")
        else:
            file_database = FileDatabase.get_instance()
            print("... database.find_local_roms")
            local_roms = file_database.find_local_roms()
            print("... walk kickstarts_dir")
            for dir_path, dir_names, file_names in os.walk(kickstarts_dir):
                for file_name in file_names:
                    if not file_name.lower().endswith(
                        ".rom"
                    ) and not file_name.lower().endswith(".bin"):
                        continue
                    path = Paths.join(dir_path, file_name)
                    if path in local_roms:
                        local_roms[path] = None
                        # already exists in database
                        continue
                    print("[startup] adding kickstart", path)
                    ROMManager.add_rom_to_database(path, file_database)
            print(local_roms)
            for path, file_id in local_roms.items():
                if file_id is not None:
                    print("[startup] removing kickstart", path)
                    file_database.delete_file(id=file_id)
            print("... commit")
            file_database.commit()
            LauncherSettings.set(
                "kickstarts_dir_mtime", cls.get_dir_mtime_str(kickstarts_dir)
            )

        amiga = Amiga.get_model_config("A500")
        for sha1 in amiga["kickstarts"]:
            if fsgs.file.find_by_sha1(sha1=sha1):
                break
        else:
            file_database = FileDatabase.get_instance()
            cls.amiga_forever_kickstart_scan()
            file_database.commit()

    @classmethod
    def amiga_forever_kickstart_scan(cls):
        for path in FSGSDirectories.get_amiga_forever_directories():
            cls.scan_dir_for_kickstarts(path)

    @staticmethod
    def scan_dir_for_kickstarts(scan_dir):
        file_database = FileDatabase.get_instance()
        for dir_path, dir_names, file_names in os.walk(scan_dir):
            for file_name in file_names:
                if not file_name.endswith(".rom"):
                    continue
                path = Paths.join(dir_path, file_name)
                if file_database.find_file(path=path):
                    continue
                print("[startup] adding kickstart", path)
                ROMManager.add_rom_to_database(path, file_database)

    @staticmethod
    def get_dir_mtime_str(path):
        try:
            return str(int(os.path.getmtime(path)))
        except Exception:
            return "0"
