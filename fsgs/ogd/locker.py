import time
from functools import lru_cache

import fsbc.settings
from fsgs.filedatabase import FileDatabase
from fsgs.LockerDatabase import LockerDatabase
from fsgs.download import Downloader
from fsgs.network import openretro_url_prefix
from fsgs.ogd.base import SynchronizerBase
from fsgs.ogd.context import SynchronizerContext
from fsgs.res import gettext


def is_locker_enabled():
    return fsbc.settings.get("database_locker") != "0"


def open_locker_uri(uri):
    sha1 = uri[9:]
    assert len(sha1) == 40
    context = SynchronizerContext()
    url = "{0}/api/locker/{1}".format(openretro_url_prefix(), sha1)
    path = Downloader.cache_file_from_url(
        url, auth=(context.username, context.password)
    )
    return path


class LockerSynchronizer(SynchronizerBase):
    def __init__(self, *args, **kwargs):
        SynchronizerBase.__init__(self, *args, **kwargs)

    def synchronize(self):
        if not is_locker_enabled():
            return
        if "locker" not in self.context.meta:
            # We haven't looked up synchronization information from the server,
            # that probably means we didn't want to synchronize with the
            # server now, therefore we just return.
            return
        if self.stop_check():
            return
        database = LockerDatabase.instance()
        sync_version = database.get_sync_version()
        if sync_version == self.context.meta["locker"]["sync"]:
            print("[SYNC] Locker data already up to date")
            return

        self.set_status(gettext("Fetching locker data..."))
        data = self.fetch_data("/api/locker-sync/1")
        assert len(data) % 20 == 0
        self.set_status(gettext("Updating locker data..."))
        database.clear()
        k = 0
        while k < len(data):
            sha1_bytes = data[k : k + 20]
            database.add_sha1_binary(sha1_bytes)
            k += 20

        database.set_sync_version(self.context.meta["locker"]["sync"])
        self.set_status(gettext("Committing locker data..."))
        self.update_file_database_timestamps()
        database.commit()

    def update_file_database_timestamps(self):
        # This isn't very elegant, but in order to force the game scanner to
        # refresh the game list based on files, we update the stamps in the
        # file database. Also, since we haven't keep track of additions /
        # deletions, we set both stamps for now...
        file_database = FileDatabase.instance()
        file_database.last_file_insert = time.time()
        file_database.last_file_delete = time.time()
        file_database.update_last_event_stamps()
        file_database.commit()
