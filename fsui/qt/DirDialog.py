from fsui.qt import Qt
from .FileDialog import FileDialog


class DirDialog(FileDialog):
    def __init__(self, parent=None, message="", directory=""):
        FileDialog.__init__(self, parent, message, directory, dir_mode=True)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
