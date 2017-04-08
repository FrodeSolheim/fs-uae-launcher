from fsbc import settings
from fsgs.drivers.mess.messsmsdriver import MessSmsDriver
from fsgs.option import Option
from fsgs.platform import PlatformHandler
from fsgs.platforms.loader import SimpleLoader
from fsgs.platforms.sms.mednafensmsdriver import MednafenSMSDriver


class MasterSystemPlatformHandler(PlatformHandler):
    PLATFORM_NAME = "Master System"

    def __init__(self):
        PlatformHandler.__init__(self)

    def get_loader(self, fsgs):
        return MasterSystemLoader(fsgs)

    def get_runner(self, fsgs):
        if settings.get(Option.SMS_DRIVER) == "mess":
            return MessSmsDriver(fsgs)
        else:
            return MednafenSMSDriver(fsgs)


class MasterSystemLoader(SimpleLoader):
    pass
