from fsgs.platform import PlatformHandler
from fsgs.dosbox.dos import DOSRunner
from .loader import SimpleLoader


class DOSPlatformHandler(PlatformHandler):

    PLATFORM_NAME = "DOS"

    def __init__(self):
        PlatformHandler.__init__(self)

    def get_loader(self, fsgs):
        return DOSLoader(fsgs)

    def get_runner(self, fsgs):
        return DOSRunner(fsgs)


class DOSLoader(SimpleLoader):

    def load_files(self, values):
        self.config["file_list"] = values["file_list"]

    def load_extra(self, values):
        self.config["hd_startup"] = values["hd_startup"]
        self.config["dosbox_cpu_cycles"] = values["dosbox_cpu_cycles"]
