from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from fsgs.platform import PlatformHandler
from fsgs.mess.atari_2600 import Atari2600Runner
from .loader import SimpleLoader


class Atari2600PlatformHandler(PlatformHandler):
    PLATFORM_NAME = "Atari 2600"

    def __init__(self):
        PlatformHandler.__init__(self)

    def get_loader(self, fsgs):
        return Atari2600Loader(fsgs)

    def get_runner(self, fsgs):
        return Atari2600Runner(fsgs)


class Atari2600Loader(SimpleLoader):
    pass
