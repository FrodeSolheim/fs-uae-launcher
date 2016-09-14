import os

import pkg_resources

import fsboot
import fsui
from fsui.qt import QFont


class Font(fsui.Font):

    def __init__(self, name, size):
        qfont = QFont(name)
        qfont.setPixelSize(size)
        super().__init__(qfont)

    @classmethod
    def stream(cls, name):
        path = os.path.join(fsboot.base_dir(), "Workspace", "Fonts", name)
        try:
            return open(path, "rb")
        except FileNotFoundError:
            return pkg_resources.resource_stream(
                "workspace.ui", "data/" + name)
