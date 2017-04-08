from fsgs.platform import PlatformHandler
from fsgs.platforms.dos.dosboxdosdriver import DosBoxDosDriver
from fsgs.platforms.loader import SimpleLoader


class DOSPlatformHandler(PlatformHandler):
    PLATFORM_NAME = "DOS"

    def __init__(self):
        super().__init__()

    def get_loader(self, fsgs):
        return DOSLoader(fsgs)

    def get_runner(self, fsgs):
        return DosBoxDosDriver(fsgs)


class DOSLoader(SimpleLoader):
    def load_files(self, values):
        self.config["file_list"] = values["file_list"]

    def load_extra(self, values):
        self.config["dosbox_cpu_cycles"] = values["dosbox_cpu_cycles"]
        self.config["dosbox_sblaster_irq"] = values["sblaster_irq"]
        # FIXME: REMOVE
        self.config["sblaster_irq"] = values["sblaster_irq"]

        self.config["command"] = values["command"]
        if not self.config["command"]:
            # Deprecated option
            self.config["command"] = values["hd_startup"]

        for key in values.keys():
            if key.startswith("dosbox_"):
                self.config[key] = values[key]
