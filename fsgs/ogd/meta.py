from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from fsbc.Application import app
from fsgs.res import gettext
from .base import SynchronizerBase


class MetaSynchronizer(SynchronizerBase):

    def __init__(self, *args, **kwargs):
        SynchronizerBase.__init__(self, *args, **kwargs)

    def synchronize(self):
        if self.stop_check():
            return

        if not app.settings["database_auth"]:
            # not logged in
            return

        self.set_status(gettext("Fetching synchronization information..."))
        self.context.meta = self.fetch_json("/api/sync/1")
