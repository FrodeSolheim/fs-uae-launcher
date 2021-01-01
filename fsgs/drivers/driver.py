from fsgs.context import FSGameSystemContext
from fsgs.platform import PlatformHandler


def create_driver_for_config(config, settings=None):
    platform = config.get("platform", "").lower()
    if not platform:
        platform = "amiga"
    platform = PlatformHandler.create(platform)
    fsgc = FSGameSystemContext()

    fsgc.config.load(config)

    if settings:
        fsgc._settings = settings

    driver = platform.driver(fsgc)
    return driver
