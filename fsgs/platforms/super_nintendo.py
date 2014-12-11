from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from fsgs.platform import PlatformHandler
from fsgs.mednafen.super_nintendo import SuperNintendoRunner
from .loader import SimpleLoader


class SuperNintendoPlatformHandler(PlatformHandler):
    PLATFORM_NAME = "Super Nintendo"

    def __init__(self):
        PlatformHandler.__init__(self)

    def get_loader(self, fsgs):
        return SuperNintendoLoader(fsgs)

    def get_runner(self, fsgs):
        return SuperNintendoRunner(fsgs)


class SuperNintendoLoader(SimpleLoader):
    pass
