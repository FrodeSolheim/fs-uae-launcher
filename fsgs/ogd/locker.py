import time
from .base import SynchronizerBase
from ..LockerDatabase import LockerDatabase
from fsgs.FileDatabase import FileDatabase
from fsgs.res import gettext


class LockerSynchronizer(SynchronizerBase):

    def __init__(self, *args, **kwargs):
        SynchronizerBase.__init__(self, *args, **kwargs)

    def synchronize(self):
        if "locker-sync" not in self.context.meta:
            # we haven't looked up synchronization information from the server,
            # that probably means we didn't want to synchronize with the
            # server now, therefore we just return
            return

        if self.stop_check():
            return

        database = LockerDatabase.instance()
        sync_version = database.get_sync_version()
        if sync_version == self.context.meta["locker-sync"]:
            print("locker already up to date")
            return

        self.set_status(gettext("Fetching locker data..."))
        data = self.fetch_data("/api/locker-sync/1")
        assert len(data) % 20 == 0

        self.set_status(gettext("Updating locker data..."))
        database.clear()

        k = 0
        while k < len(data):
            sha1_bytes = data[k:k + 20]
            database.add_sha1_binary(sha1_bytes)
            k += 20

        database.set_sync_version(self.context.meta["locker-sync"])

        self.set_status(gettext("Committing locker data..."))

        # This isn't very elegant, but in order to force the game scanner to
        # refresh the game list based on files, we update the stamps in the
        # file database. Also, since we haven't keep track of additions /
        # deletions, we set both stamps for now...

        file_database = FileDatabase.instance()
        file_database.last_file_insert = time.time()
        file_database.last_file_delete = time.time()
        file_database.update_last_event_stamps()
        file_database.commit()

        database.commit()
