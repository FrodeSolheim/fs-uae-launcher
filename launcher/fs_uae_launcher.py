import hashlib
import os
import sys
import traceback
from collections import defaultdict
from configparser import ConfigParser, NoSectionError

import fsbc.fs as fs
import fsui
from fsbc.application import app
from fsbc.settings import Settings
from fsbc.task import Task
from fsbc.util import unused, is_uuid
from fsgs.FSGSDirectories import FSGSDirectories
from fsgs.amiga.Amiga import Amiga
from fsgs.application import ApplicationMixin
from fsgs.context import fsgs
from fsgs.download import Downloader
from fsgs.input.enumeratehelper import EnumerateHelper
from fsgs.platform import PlatformHandler
from launcher.i18n import gettext
from launcher.launcher_config import LauncherConfig
from launcher.launcher_settings import LauncherSettings
from launcher.startup_scan import StartupScan
from launcher.ui.config.HardDriveGroup import HardDriveGroup
from launcher.ui.download import DownloadGameWindow, DownloadTermsDialog
from launcher.ui.launch import LaunchDialog
from launcher.ui.launcher_window import LauncherWindow


class FSUAELauncher(ApplicationMixin, fsui.Application):
    def __init__(self):
        fsui.Application.__init__(self, "fs-uae-launcher")
        self.set_icon(fsui.Icon("fs-uae-launcher", "pkg:launcher"))
        self.fsgs = fsgs

    def on_idle(self):
        self.fsgs.signal.process()

    @classmethod
    def pre_start(cls):
        print("FSUAELauncherApplication.pre_start")
        cls.load_settings()
        StartupScan.config_startup_scan()
        StartupScan.kickstart_startup_scan()
        # FIXME: should now sanitize check some options -for instance,
        # - check if configured joysticks are still connected
        # - check if paths still exists, etc
        # Config.update_kickstart()
        cls.load_plugins()

    @classmethod
    def start(cls):
        cls.pre_start()
        print("FSUAELauncherApplication.start")

        if cls.run_config_or_game():
            return False
        # window = LauncherWindow(fsgs)
        # window.show()
        LauncherWindow.open()
        return True

    @classmethod
    def run_config_or_game(cls):
        config_path = None
        archive_path = None
        floppy_image_path = None
        config_uuid = None

        # FIXME: replace argument "parsing" with use of argparse module
        # at some point

        if sys.argv[-1].endswith(".fs-uae"):
            config_path = sys.argv[-1]
        elif sys.argv[-1].endswith(".zip"):
            archive_path = sys.argv[-1]
        elif sys.argv[-1].endswith(".lha"):
            archive_path = sys.argv[-1]
        elif sys.argv[-1].endswith(".adf"):
            # FIXME: support / check for other disk images as well
            floppy_image_path = sys.argv[-1]
        elif is_uuid(sys.argv[-1]):
            config_uuid = sys.argv[-1].lower()

        if config_path:
            print("config path given:", config_path)
            if not os.path.exists(config_path):
                print("config path does not exist", file=sys.stderr)
                return True
            LauncherConfig.load_file(config_path)
            fsgs.config.add_from_argv()
            LauncherSettings.set("parent_uuid", "")
            cls.start_game()
            return True

        elif archive_path:
            print("archive path given:", archive_path)
            if not os.path.exists(archive_path):
                print("archive path does not exist", file=sys.stderr)
                return True
            # FIXME: if archive is determined to contain (only) floppy disk
            # images, load those into floppy drives instead
            values = HardDriveGroup.generate_config_for_archive(archive_path)
            values["hard_drive_0"] = archive_path
            LauncherConfig.load(values)
            fsgs.config.add_from_argv()
            LauncherSettings.set("parent_uuid", "")
            cls.start_game()
            return True

        elif floppy_image_path:
            values = {
                "floppy_drive_0": floppy_image_path,
            }
            LauncherConfig.load(values)
            fsgs.config.add_from_argv()
            LauncherSettings.set("parent_uuid", "")
            cls.start_game()
            return True

        elif config_uuid:
            print("config uuid given:", config_uuid)
            variant_uuid = config_uuid
            # values = fsgs.game.set_from_variant_uuid(variant_uuid)
            if fsgs.load_game_variant(variant_uuid):
                print("loaded variant")
            else:
                print("could not load variant, try to load game")
                game_uuid = config_uuid
                variant_uuid = fsgs.find_preferred_game_variant(game_uuid)
                print("preferred variant:", variant_uuid)
                fsgs.load_game_variant(variant_uuid)
            fsgs.config.add_from_argv()
            cls.start_game()
            return True

    _plugins_loaded = False

    @classmethod
    def load_plugins(cls):
        if cls._plugins_loaded:
            return
        cls._plugins_loaded = True

        plugins_dir = FSGSDirectories.get_plugins_dir()
        if plugins_dir:
            dont_write_bytecode = sys.dont_write_bytecode
            try:
                cls._load_plugins(plugins_dir)
            finally:
                sys.dont_write_bytecode = dont_write_bytecode

    @staticmethod
    def _load_plugins(plugins_dir):
        print("loading plugins")
        for full_name in os.listdir(plugins_dir):
            name, ext = os.path.splitext(full_name)
            if ext.lower() != ".py":
                continue
            path = os.path.join(plugins_dir, full_name)
            print("loading", path)
            name = "plugin_" + hashlib.sha1(path.encode("UTF-8")).hexdigest()
            print(name)

            # noinspection PyDeprecation
            import imp
            try:
                # noinspection PyDeprecation
                plugin = imp.load_source(name, path)
                print("name:", getattr(plugin, "name", ""))
                print("version:", getattr(plugin, "version", ""))
                plugin.fsgs = fsgs
                plugin.plugin_dir = os.path.dirname(path)
                plugin.fsgs_init()
            except Exception:
                traceback.print_exc()
                continue
            else:
                print(name, "initialized")

    settings_loaded = False

    @classmethod
    def load_settings(cls):
        if cls.settings_loaded:
            return
        cls.settings_loaded = True

        settings = Settings.instance()
        settings.load()
        path = settings.path
        # path = app.get_settings_path()
        print("loading last config from " + repr(path))
        if not os.path.exists(path):
            print("settings file does not exist")
        # noinspection PyArgumentList
        cp = ConfigParser(interpolation=None)
        try:
            cp.read([path])
        except Exception as e:
            print(repr(e))
            return

        for key in LauncherSettings.old_keys:
            if app.settings.get(key):
                print("[SETTINGS] Removing old key", key)
                app.settings.set(key, "")

        if fsgs.config.add_from_argv():
            print("[CONFIG] Configuration specified via command line")
            # Prevent the launcher from loading the last used game
            LauncherSettings.set("parent_uuid", "")
        elif LauncherSettings.get("config_path"):
            if LauncherConfig.load_file(LauncherSettings.get("config_path")):
                print("[CONFIG] Loaded last configuration file")
            else:
                print("[CONFIG] Failed to load last configuration file")
                LauncherConfig.load_default_config()

            # config = {}
            # try:
            #     keys = cp.options("config")
            # except NoSectionError:
            #     keys = []
            # for key in keys:
            #     config[key] = fs.from_utf8_str(cp.get("config", key))
            # for key, value in config.items():
            #     print("loaded", key, value)
            #     fsgs.config.values[key] = value

    @staticmethod
    def save_settings():
        extra = {}
        for key, value in fsgs.config.values.items():
            if key.startswith("__"):
                # keys starting with __ are never saved
                continue
            extra["config/" + str(key)] = str(value)
        app.settings.save(extra=extra)

    @classmethod
    def start_game(cls):
        from .netplay.netplay import Netplay
        if Netplay.current() and Netplay.current().game_channel:
            Netplay.current().start_netplay_game()
        else:
            cls.start_local_game()

    @classmethod
    def start_local_game(cls):
        print("START LOCAL GAME")
        print("x_missing_files", LauncherConfig.get("x_missing_files"))

        if LauncherConfig.get("x_missing_files"):
            if LauncherConfig.get("download_file"):
                if LauncherConfig.get("download_terms") and not \
                        Downloader.check_terms_accepted(
                            LauncherConfig.get("download_file"),
                            LauncherConfig.get("download_terms")):
                    from .ui.launcher_window import LauncherWindow
                    dialog = DownloadTermsDialog(LauncherWindow.current(), fsgs)
                    if not dialog.show_modal():
                        return

            elif LauncherConfig.get("download_page"):
                from .ui.launcher_window import LauncherWindow
                # fsui.show_error(_("This game must be downloaded first."))
                DownloadGameWindow(LauncherWindow.current(), fsgs).show()
                return
            else:
                fsui.show_error(
                    gettext("This game variant cannot be started "
                            "because you don't have all required files."))
                return

        platform_id = LauncherConfig.get("platform").lower()
        amiga_platform = platform_id in ["", "amiga", "cdtv", "cd32"]
        if amiga_platform:
            cls.start_local_game_amiga()
        else:
            cls.start_local_game_other()

    @classmethod
    def start_local_game_other(cls):
        database_name = LauncherConfig.get("__database")
        variant_uuid = LauncherConfig.get("variant_uuid")
        assert variant_uuid

        fsgs.game.set_from_variant_uuid(database_name, variant_uuid)
        platform_handler = PlatformHandler.create(fsgs.game.platform.id)
        runner = platform_handler.get_runner(fsgs)

        task = RunnerTask(runner)
        from .ui.launcher_window import LauncherWindow
        dialog = LaunchDialog(
            LauncherWindow.current(), gettext("Launching Game"), task)
        dialog.show()

        LauncherConfig.set("__running", "1")
        task.start()
        # dialog.show_modal()
        # dialog.close()

    @classmethod
    def start_local_game_amiga(cls):
        # make sure x_kickstart_file is initialized
        LauncherConfig.set_kickstart_from_model()

        # if not Config.get("x_kickstart_file"):  # or not \
        #     #  os.path.exists(Config.get("kickstart_file")):
        #     fsui.show_error(
        #         gettext("No kickstart found for this model. Use the 'Import "
        #                 "Kickstarts' function from the menu."))
        #     return
        cs = Amiga.get_model_config(
            LauncherConfig.get("amiga_model"))["ext_roms"]
        if len(cs) > 0:
            # extended kickstart ROM is needed
            if not LauncherConfig.get("x_kickstart_ext_file"):
                fsui.show_error(
                    gettext("No extended kickstart found for this model. "
                            "Try 'scan' function."))
                return

        config = LauncherConfig.copy()
        prepared_config = cls.prepare_config(config)

        model = LauncherConfig.get("amiga_model")
        if model.startswith("CD32"):
            platform = "CD32"
        elif model == "CDTV":
            platform = "CDTV"
        else:
            platform = "Amiga"
        name = LauncherSettings.get("config_name")
        uuid = LauncherConfig.get("x_game_uuid")

        from fsgs.SaveStateHandler import SaveStateHandler
        save_state_handler = SaveStateHandler(fsgs, name, platform, uuid)

        from fsgs.amiga.LaunchHandler import LaunchHandler
        launch_handler = LaunchHandler(fsgs, name, prepared_config,
                                       save_state_handler)

        from .ui.launcher_window import LauncherWindow
        task = AmigaLaunchTask(launch_handler)
        # dialog = LaunchDialog(MainWindow.instance, launch_handler)
        dialog = LaunchDialog(
            LauncherWindow.current(), gettext("Launching FS-UAE"), task)
        dialog.show()

        def on_show_license_information(license_text):
            unused(license_text)
            # FIXME: don't depend on wx here
            # noinspection PyUnresolvedReferences
            # import wx
            # license_dialog = wx.MessageDialog(
            #     dialog, license_text, _("Terms of Use"),
            #     wx.OK | wx.CANCEL | wx.CENTRE)
            # license_dialog.CenterOnParent()
            # result = license_dialog.ShowModal()
            # return result == wx.ID_OK
            # FIXME
            return True

        fsgs.file.on_show_license_information = on_show_license_information

        LauncherConfig.set("__running", "1")
        task.start()
        # dialog.show_modal()
        # dialog.close()

    @classmethod
    def prepare_config(cls, original_config):
        config = defaultdict(str)
        for key, value in LauncherSettings.items():
            # We now show warnings on status bar instead
            # if key in LauncherConfig.config_keys:
            #     print("... ignoring config key from settings:", key)
            #     continue
            config[key] = value

        config["base_dir"] = FSGSDirectories.get_base_dir()

        for key, value in original_config.items():
            if value:
                config[key] = value

        if not config["joystick_port_0_mode"]:
            config["joystick_port_0_mode"] = "mouse"
        if not config["joystick_port_1_mode"]:
            if config["amiga_model"].startswith("CD32"):
                config["joystick_port_1_mode"] = "cd32 gamepad"
            else:
                config["joystick_port_1_mode"] = "joystick"
        if not config["joystick_port_2_mode"]:
            config["joystick_port_2_mode"] = "none"
        if not config["joystick_port_3_mode"]:
            config["joystick_port_3_mode"] = "none"

        from .device_manager import DeviceManager
        devices = DeviceManager.get_devices_for_ports(config)
        for port in range(4):
            key = "joystick_port_{0}".format(port)
            if not config.get(key):
                # key not set, use calculated default value
                config[key] = devices[port].id

        for remove_key in ["database_username", "database_password",
                           "database_username", "database_email",
                           "database_auth", "device_id"]:
            if remove_key in config:
                del config[remove_key]

        # overwrite netplay config

        if config.get("__netplay_host", ""):
            config["netplay_server"] = config["__netplay_host"]
        if config.get("__netplay_password", ""):
            config["netplay_password"] = config["__netplay_password"]
        if config.get("__netplay_port", ""):
            config["netplay_port"] = config["__netplay_port"]

        # copy actual kickstart options from x_ options

        config["kickstart_file"] = config["x_kickstart_file"]
        config["kickstart_ext_file"] = config["x_kickstart_ext_file"]

        if not config["kickstart_file"]:
            # Warning will have been shown on the status bar
            config["kickstart_file"] = "internal"

        # Copy default configuration values from model defaults. The main
        # purpose of this is to let the launch code know about implied defaults
        # so it can for example configure correct ROM files for expansions.

        model_config = Amiga.get_current_config(config)
        for key, value in model_config["defaults"].items():
            if not config.get(key):
                config[key] = value

        # make sure FS-UAE does not load other config files (Host.fs-uae)
        config["end_config"] = "1"

        if config.get("__netplay_game", ""):
            print("\nfixing config for netplay game")
            for key in [x for x in config.keys() if x.startswith("uae_")]:
                print("* removing option", key)
                del config[key]

        return config


# FIXME: Files to clean up:
# Documents/FS-UAE/Cache/File Database.sqlite
# Documents/FS-UAE/Data/Game Database.sqlite
# Documents/FS-UAE/Data/Launcher.sqlite
# Documents/FS-UAE/Logs/FS-UAE.log
# Documents/FS-UAE/Logs/FS-UAE.log.txt
# Documents/FS-UAE/Data/Database.sqlite
# Documents/FS-UAE/Cache/Files.sqlite
# Documents/FS-UAE/Cache/Locker.sqlite
# Documents/FS-UAE/Cache/oagd.net.sqlite
# Documents/FS-UAE/Cache/Games.sqlite


class AmigaLaunchTask(Task):
    def __init__(self, launch_handler):
        Task.__init__(self, "Amiga Launch Task")
        self.launch_handler = launch_handler

    def run(self):
        self.launch_handler.run_sequence()


class RunnerTask(Task):
    def __init__(self, runner):
        Task.__init__(self, "Runner Task")
        self.runner = runner

    def run(self):
        device_helper = EnumerateHelper()
        device_helper.default_port_selection(self.runner.ports)

        self.runner.prepare()
        self.set_progress("__run__")
        process = self.runner.run()
        process.wait()
        self.runner.finish()
