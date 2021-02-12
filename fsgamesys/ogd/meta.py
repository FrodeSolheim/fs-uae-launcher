from fsbc.application import app
from fsgamesys.ogd.base import SynchronizerBase
from fsgamesys.res import gettext


class MetaSynchronizer(SynchronizerBase):
    def __init__(self, *args, **kwargs):
        SynchronizerBase.__init__(self, *args, **kwargs)

    def synchronize(self):
        if self.stop_check():
            return
        # if not app.settings["database_auth"]:
        #     # not logged in
        #     return
        self.set_status(gettext("Fetching synchronization information..."))
        self.context.meta = self.fetch_json("/api/sync")
