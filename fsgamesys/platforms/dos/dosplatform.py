from fsgamesys.platforms.dos.dosboxdosdriver import DosBoxDosDriver
from fsgamesys.platforms.loader import SimpleLoader
from fsgamesys.platforms.platform import PlatformHandler


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
        self.config["cue_sheets"] = values["cue_sheets"]

    def load_extra(self, values):
        for key in values.keys():
            if key.startswith("dosbox_"):
                self.config[key] = values[key]
        # for key in ["dosbox_cpu_cycles", "dosbox_sblaster_sbtype",
        #             "dosbox_sblaster_sbbase", "dosbox_sblaster_irq",
        #             "dosbox_sblaster_oplrate"]:
        #     self.config[key] = values[key]

        self.config["command"] = values["command"]
        if not self.config["command"]:
            # Deprecated option
            self.config["command"] = values["hd_startup"]
