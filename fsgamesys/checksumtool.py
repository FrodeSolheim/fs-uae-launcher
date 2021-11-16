import hashlib
import os
from typing import Optional

from fsgamesys.amiga.rommanager import ROMManager
from fsgamesys.archive import Archive
from fsui import TopLevelWidget

EMPTY_SHA1 = "da39a3ee5e6b4b0d3255bfef95601890afd80709"

# FIXME: Move to Launcher?
class ChecksumTool:
    def __init__(self, parent: Optional[TopLevelWidget] = None):
        self.parent = parent
        # fsui.Window.__init__(self, parent, "Checksumming")
        # self.layout = fsui.VerticalLayout()
        # label = fsui.HeadingLabel(self, "Checksumming file...")
        # self.layout.add(label, fill=True)
        # self.layout.add_spacer(6)
        # #self.center_on_parent()

    def checksum(self, path: str) -> str:
        print("[CHECKSUM]", repr(path))
        archive = Archive(path)
        if os.path.exists(path):
            size = os.path.getsize(path)
            if size == 0:
                # Either a real 0-byte file or a device node on a BSD
                # system (could be large). To reliably get the size we could
                # use ioctl, but we simply return the checksum for a 0-byte
                # file in either case.
                return EMPTY_SHA1
        s = hashlib.sha1()
        f = archive.open(path)
        while True:
            data = f.read(65536)
            if not data:
                break
            s.update(data)
        return s.hexdigest()

    def checksum_rom(self, path: str) -> str:
        print("[CHECKSUM] ROM:", repr(path))
        archive = Archive(path)
        return ROMManager.decrypt_archive_rom(archive, path).sha1
