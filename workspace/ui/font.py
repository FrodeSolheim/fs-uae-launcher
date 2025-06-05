import os

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
            raise NotImplementedError()
