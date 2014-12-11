from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from fsgs.platform import PlatformHandler
from fsgs.mednafen.master_system import MasterSystemRunner
from .loader import SimpleLoader


class MasterSystemPlatformHandler(PlatformHandler):
    PLATFORM_NAME = "Master System"

    def __init__(self):
        PlatformHandler.__init__(self)

    def get_loader(self, fsgs):
        return MasterSystemLoader(fsgs)

    def get_runner(self, fsgs):
        return MasterSystemRunner(fsgs)


class MasterSystemLoader(SimpleLoader):
    pass
