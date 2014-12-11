from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from fsui.qt import Qt
from .FileDialog import FileDialog


class DirDialog(FileDialog):

    def __init__(
            self, parent=None, message="", directory=""):
        FileDialog.__init__(self, parent, message, directory, dir_mode=True)
        self.setAttribute(Qt.WA_DeleteOnClose)
