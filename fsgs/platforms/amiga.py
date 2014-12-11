from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from fsgs.platform import PlatformHandler
from fsgs.amiga.ValueConfigLoader import ValueConfigLoader
from fsgs.amiga.runner import AmigaRunner


class AmigaPlatformHandler(PlatformHandler):
    PLATFORM_NAME = "Amiga"

    def __init__(self):
        PlatformHandler.__init__(self)

    def get_loader(self, fsgs):
        loader = ValueConfigLoader()
        loader.uuid = fsgs.game.variant.uuid
        return loader

    def get_runner(self, fsgs):
        return AmigaRunner(fsgs)
