from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from fsgs.platforms.amiga import AmigaPlatformHandler


class CD32PlatformHandler(AmigaPlatformHandler):
    PLATFORM_NAME = "CD32"

    def __init__(self):
        AmigaPlatformHandler.__init__(self)
