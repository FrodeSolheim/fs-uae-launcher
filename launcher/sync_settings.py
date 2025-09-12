import configparser
import os
from fsgs.amiga.amiga import Amiga

SYNC_CONFIG_PATH = os.path.expanduser("~/.netplay_sync_config.ini")

class SyncSettings:
    def __init__(self):
        self.load()

    def load(self):
        config = configparser.ConfigParser()
        config.read(SYNC_CONFIG_PATH)
        sync = config["sync"] if "sync" in config else {}
        self.MAX_FLOPPY_DRIVES = int(sync.get("Max Floppy Drives", Amiga.MAX_FLOPPY_DRIVES))
        self.MAX_FLOPPY_IMAGES = int(sync.get("Max Floppy Images", Amiga.MAX_FLOPPY_IMAGES))
        self.MAX_CDROM_DRIVES = int(sync.get("Max CDROM Drives", Amiga.MAX_CDROM_DRIVES))
        self.MAX_CDROM_IMAGES = int(sync.get("Max CDROM Images", Amiga.MAX_CDROM_IMAGES))
        self.MAX_HARD_DRIVES = int(sync.get("Max Hard Drives", Amiga.MAX_HARD_DRIVES))

    def update(self):
        self.load()

# Create a global instance
sync_settings = SyncSettings()
