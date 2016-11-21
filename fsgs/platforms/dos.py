from fsgs.drivers.dos import DOSDriver
from fsgs.platform import PlatformHandler
from fsgs.platforms.loader import SimpleLoader


class DOSPlatformHandler(PlatformHandler):
    PLATFORM_NAME = "DOS"

    def __init__(self):
        super().__init__()

    def get_loader(self, fsgs):
        return DOSLoader(fsgs)

    def get_runner(self, fsgs):
        return DOSDriver(fsgs)


class DOSLoader(SimpleLoader):
    def load_files(self, values):
        self.config["file_list"] = values["file_list"]

    def load_extra(self, values):
        for key in ["hd_startup", "dosbox_cpu_cycles", "sblaster_irq"]:
            self.config[key] = values[key]
