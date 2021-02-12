import time

from fsbc.application import app
from fsbc.signal import Signal
from fsbc.task import Task
from fsgamesys.Database import Database
from fsgamesys.ogd.context import SynchronizerContext
from fsgamesys.ogd.lists import ListsSynchronizer
from fsgamesys.ogd.meta import MetaSynchronizer


class DatabaseRefreshTask(Task):
    def __init__(self):
        Task.__init__(self, "DatabaseRefreshTask")

    # def stop_check(self):
    #     pass

    def on_status(self, status):
        self.progressed(status)

    def run(self):
        with Database.get_instance() as database:
            self._run(database)

    def _run(self, database):
        # FIXME, dependency on fs_uae_launcher
        # from fs_uae_launcher.Scanner import Scanner
        # Scanner.start([], scan_for_files=False, update_game_database=True)
        from fsgamesys.ogd.game_rating_synchronizer import GameRatingSynchronizer
        from launcher.gamescanner import GameScanner

        context = SynchronizerContext()

        synchronizer = MetaSynchronizer(
            context, on_status=self.on_status, stop_check=self.stop_check
        )
        synchronizer.synchronize()

        synchronizer = GameRatingSynchronizer(
            context,
            database,
            on_status=self.on_status,
            stop_check=self.stop_check,
        )
        synchronizer.username = "auth_token"
        synchronizer.password = app.settings["database_auth"]
        synchronizer.synchronize()

        synchronizer = ListsSynchronizer(
            context, on_status=self.on_status, stop_check=self.stop_check
        )
        synchronizer.synchronize()

        scanner = GameScanner(
            context, None, on_status=self.on_status, stop_check=self.stop_check
        )
        scanner.update_game_database()
        scanner.scan(database)

        # FIXME: review what signals should be sent when a scan is performed
        # FIXME: these should be removed soon
        app.settings["last_scan"] = str(time.time())
        app.settings["__config_refresh"] = str(time.time())
        # this must be called from main, since callbacks are broadcast
        # when settings are changed
        Signal("scan_done").notify()
