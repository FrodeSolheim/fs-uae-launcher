from fsgamesys.platforms.amiga import AmigaPlatformHandler


class CDTVPlatformHandler(AmigaPlatformHandler):
    PLATFORM_NAME = "CDTV"

    def __init__(self):
        AmigaPlatformHandler.__init__(self)
