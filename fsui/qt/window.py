from .qt import QMainWindow
from .windowbase import WindowBase


class Window(WindowBase(QMainWindow)):

    def __init__(self, parent=None, title="", border=True):
        super().__init__(parent, title=title, border=border)


import sys
if "--workspace" in sys.argv:
    fs_uae_workspace = __import__("fs_uae_workspace.window")
    if "--windows" not in sys.argv:
        from fs_uae_workspace.window import Window
