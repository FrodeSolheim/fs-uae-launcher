from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from fsgs.platform import PlatformHandler
from fsgs.mess.atari_7800 import Atari7800Runner
from .loader import SimpleLoader


class Atari7800PlatformHandler(PlatformHandler):
    PLATFORM_NAME = "Atari 7800"

    def __init__(self):
        PlatformHandler.__init__(self)

    def get_loader(self, fsgs):
        return Atari7800Loader(fsgs)

    def get_runner(self, fsgs):
        return Atari7800Runner(fsgs)


class Atari7800Loader(SimpleLoader):
    pass
