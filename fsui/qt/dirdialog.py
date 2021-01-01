from fsui.qt.filedialog import FileDialog
from fsui.qt.qt import Qt


class DirDialog(FileDialog):
    def __init__(self, parent=None, message="", directory=""):
        FileDialog.__init__(self, parent, message, directory, dir_mode=True)
        self.setAttribute(Qt.WA_DeleteOnClose)
