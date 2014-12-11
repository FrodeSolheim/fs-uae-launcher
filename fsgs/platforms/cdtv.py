from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from fsgs.platforms.amiga import AmigaPlatformHandler


class CDTVPlatformHandler(AmigaPlatformHandler):
    PLATFORM_NAME = "CDTV"

    def __init__(self):
        AmigaPlatformHandler.__init__(self)
