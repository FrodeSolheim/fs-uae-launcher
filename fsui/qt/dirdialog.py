from typing import Optional

from fsui.qt.filedialog import FileDialog
from fsui.qt.qt import Qt
from fsui.qt.toplevelwidget import TopLevelWidget


class DirDialog(FileDialog):
    def __init__(
        self,
        parent: Optional[TopLevelWidget] = None,
        message: str = "",
        directory: str = "",
    ) -> None:
        FileDialog.__init__(self, parent, message, directory, dir_mode=True)
        self.setAttribute(Qt.WA_DeleteOnClose)
