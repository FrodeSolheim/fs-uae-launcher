import hashlib

import fsui
from fsbc.util import unused
from fswidgets.widget import Widget

from ..i18n import gettext


class ChecksumDialog(fsui.Window):
    def __init__(self, parent: Widget, path: str):
        unused(path)
        fsui.Window.__init__(self, parent, gettext("Checksumming"))
        self.layout = fsui.VerticalLayout()

        label = fsui.HeadingLabel(self, gettext("Checksumming file..."))
        self.layout.add(label, fill=True)
        self.layout.add_spacer(6)
        # self.center_on_parent()

    @staticmethod
    def checksum(path: str):
        s = hashlib.sha1()
        with open(path, "rb") as f:
            data = f.read()
            while data:
                s.update(data)
                data = f.read()
        return s.hexdigest()
