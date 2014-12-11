from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import six
import time
import threading
import traceback
from fsgs.Database import Database
from fsgs.ogd.context import SynchronizerContext
from fsgs.ogd.meta import MetaSynchronizer
import fsui as fsui
from .FileScanner import FileScanner
from .ConfigurationScanner import ConfigurationScanner
from .Config import Config
from .GameScanner import GameScanner
from .Settings import Settings
from .Signal import Signal

from .GameRatingSynchronizer import GameRatingSynchronizer
from fsgs.ogd.lists import ListsSynchronizer


class Scanner:

    running = False
    stop_flag = False
    status = ("", "")
    error = ""
    paths = []
    update_game_database = False
    purge_other_dirs = False
    scan_for_files = False

    @classmethod
    def stop_check(cls):
        return cls.stop_flag

    @classmethod
    def scan_thread(cls):
        try:
            with Database.get_instance() as database:
                cls._scan_thread(database)
        except Exception as e:
            cls.error = six.text_type(e)
            traceback.print_exc()
        # else:
        #     if cls.on_status:
        #         cls.on_status(("", _("Committing data...")))
        #     database.commit()

        def on_done():
            # FIXME: these should be removed soon
            Settings.set("last_scan", str(time.time()))
            Settings.set("config_refresh", str(time.time()))

            # this must be called from main, since callbacks are broadcast
            # when settings are changed

            Signal.broadcast("scan_done")
            Config.update_kickstart()
        # call on_done from main thread
        fsui.call_after(on_done)
        cls.running = False

    @classmethod
    def _scan_thread(cls, database):
        if cls.scan_for_files:
            scanner = FileScanner(
                cls.paths, cls.purge_other_dirs, on_status=cls.on_status,
                stop_check=cls.stop_check)
            scanner.scan()
            if cls.stop_check():
                return

        # if cls.scan_for_configs or
        # if cls.update_game_database:
        scanner = ConfigurationScanner(
            cls.paths, on_status=cls.on_status, stop_check=cls.stop_check)
        scanner.scan(database)

        if cls.update_game_database:

            context = SynchronizerContext()

            synchronizer = MetaSynchronizer(
                context, on_status=cls.on_status, stop_check=cls.stop_check)
            synchronizer.synchronize()

            synchronizer = GameRatingSynchronizer(
                context, database, on_status=cls.on_status,
                stop_check=cls.stop_check)
            synchronizer.username = "auth_token"
            synchronizer.password = Settings.get("database_auth")
            synchronizer.synchronize()

            synchronizer = ListsSynchronizer(
                context, on_status=cls.on_status, stop_check=cls.stop_check)
            synchronizer.synchronize()

            scanner = GameScanner(
                context, cls.paths, on_status=cls.on_status,
                stop_check=cls.stop_check)
            scanner.update_game_database(database)

        scanner = GameScanner(
            None, cls.paths, on_status=cls.on_status,
            stop_check=cls.stop_check)
        scanner.scan(database)

    @classmethod
    def start(cls, paths, scan_for_files=True, update_game_database=False,
              purge_other_dirs=False):
        print("Scanner.start")
        if cls.running:
            print("scan already in progress")
            return
        cls.paths = paths[:]
        cls.running = True
        cls.error = ""
        cls.stop_flag = False
        cls.status = ("", "")
        #cls.scan_for_roms = scan_for_roms
        cls.scan_for_files = scan_for_files
        cls.purge_other_dirs = purge_other_dirs
        #cls.scan_for_configs = scan_for_configs
        cls.update_game_database = update_game_database
        threading.Thread(target=cls.scan_thread, name="ScannerThread").start()

    @classmethod
    def on_status(cls, status):
        cls.status = status
