from fsbc import settings
from fsgs.drivers.mess.messsmddriver import MessSmdDriver
from fsgs.option import Option
from fsgs.platform import PlatformHandler
from fsgs.platforms.loader import SimpleLoader
from fsgs.platforms.smd.mednafensmddriver import MednafenSmdDriver


class MegaDrivePlatformHandler(PlatformHandler):
    PLATFORM_NAME = "Mega Drive"

    def __init__(self):
        PlatformHandler.__init__(self)

    def get_loader(self, fsgs):
        return MegaDriveLoader(fsgs)

    def get_runner(self, fsgs):
        if settings.get(Option.SMD_DRIVER) == "mess":
            return MessSmdDriver(fsgs)
        else:
            return MednafenSmdDriver(fsgs)


class MegaDriveLoader(SimpleLoader):
    def load_extra(self, values):
        self.config[Option.SMD_MODEL] = values["model"]
        if not self.config[Option.SMD_MODEL]:
            variant = values["variant_name"].lower()
            if "world" in variant or "usa" in variant:
                model = "ntsc-u"
            elif "europe" in variant or "australia" in variant:
                model = "pal"
            elif "japan" in variant:
                model = "ntsc-j"
            else:
                model = "auto"
            self.config[Option.SMD_MODEL] = model
