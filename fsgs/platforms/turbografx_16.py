from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from fsgs.platform import PlatformHandler
from fsgs.mednafen.turbografx_16 import TurboGrafx16Runner
from .loader import SimpleLoader


class TurboGrafx16PlatformHandler(PlatformHandler):
    PLATFORM_NAME = "TurboGrafx-16"

    def __init__(self):
        PlatformHandler.__init__(self)

    def get_loader(self, fsgs):
        return TurboGrafx16Loader(fsgs)

    def get_runner(self, fsgs):
        return TurboGrafx16Runner(fsgs)


class TurboGrafx16Loader(SimpleLoader):
    pass
