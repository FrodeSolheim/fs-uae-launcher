from fsgamesys.platforms.amiga import AmigaPlatformHandler


class CD32PlatformHandler(AmigaPlatformHandler):
    PLATFORM_NAME = "CD32"

    def __init__(self):
        AmigaPlatformHandler.__init__(self)
