import sys

from fsbc import settings
from fsgs.option import Option


class ArcadeSettings:
    def __init__(self):
        # FIXME: Add fs game context as parameter and check settings through
        # that instead.
        pass

    def search(self):
        if "--disable-search" in sys.argv:
            return False
        return settings.get(Option.ARCADE_SEARCH) != "0"

    def shutdown_command(self):
        return settings.get(Option.ARCADE_SHUTDOWN)


class GameCenterSettings:
    @classmethod
    def get_shutdown_command(cls):
        return ArcadeSettings().shutdown_command()
