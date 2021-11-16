from enum import Enum
from typing import List, Optional, Union

from fsui.qt.qparent import QParent
from fsui.qt.qt import QFileDialog
from fsui.qt.toplevelwidget import TopLevelWidget


class FileDialogPickWhat(Enum):
    FILE = 0
    FILES = 1
    DIRECTORY = 2


FILE = FileDialogPickWhat.FILE
FILES = FileDialogPickWhat.FILES
DIRECTORY = FileDialogPickWhat.DIRECTORY
NATIVE_DIALOGS = True


class FileDialog(QFileDialog):
    def __init__(
        self,
        parent: Optional[TopLevelWidget] = None,
        message: str = "",
        directory: str = "",
        file: str = "",
        pattern: str = "*.*",
        multiple: bool = False,
        dir_mode: bool = False,
    ) -> None:
        QFileDialog.__init__(self, QParent(parent), message)
        if directory:
            self.setDirectory(directory)
        if dir_mode:
            self.setFileMode(QFileDialog.Directory)
        if multiple:
            self.setFileMode(QFileDialog.ExistingFiles)
        # self.setWindowFlags()

    def __del__(self) -> None:
        print("FileDialog.__del__")

    def get_path(self) -> str:
        return self.get_paths()[0]

    def get_paths(self) -> List[str]:
        return self.selectedFiles()

    def show_modal(self) -> int:
        result = self.exec_()
        print("File dialog result is", result)
        return result

    # def show(self):
    #     return self.show_modal()


def pick_directory(
    parent: Optional[TopLevelWidget] = None,
    message: str = "",
    directory: str = "",
) -> Optional[str]:
    result = pick_file(
        parent=parent, message=message, directory=directory, what=DIRECTORY
    )
    if result is None:
        return None
    assert isinstance(result, str)
    return result


def pick_file(
    parent: Optional[TopLevelWidget] = None,
    message: str = "",
    directory: str = "",
    what: FileDialogPickWhat = FILE,
) -> Union[List[str], str, None]:
    result: Union[List[str], str, None]
    if NATIVE_DIALOGS:
        if what == DIRECTORY:
            result = QFileDialog.getExistingDirectory(
                QParent(parent), message, directory
            )
        elif what == FILES:
            # Return value is fileNames, selectedFilter
            fileNames, _ = QFileDialog.getOpenFileNames(
                QParent(parent), message, directory
            )
            result = fileNames
        else:
            # Return value is fileName, selectedFilter
            fileName, _ = QFileDialog.getOpenFileName(
                QParent(parent), message, directory
            )
            result = fileName
        # if isinstance(result, tuple):
        #     # PySide returns a tuple, path is first param
        #     result = result[0]
    else:
        dialog = QFileDialog(QParent(parent), message)
        if directory:
            dialog.setDirectory(directory)
        if what == DIRECTORY:
            dialog.setFileMode(QFileDialog.Directory)
        elif what == FILES:
            dialog.setFileMode(QFileDialog.ExistingFiles)
        modal_result = dialog.exec_()
        if not modal_result:
            result = None
        elif what == FILES:
            result = dialog.selectedFiles()
        else:
            result = dialog.selectedFiles()[0]
        dialog.destroy()
    print("return file/dir dialog result:", result)
    return result


def pick_files(
    parent: Optional[TopLevelWidget] = None,
    message: str = "",
    directory: str = "",
    what: FileDialogPickWhat = FILE,
) -> Optional[List[str]]:
    result = pick_file(
        parent=parent, message=message, directory=directory, what=FILES
    )
    if result is None:
        return None
    assert isinstance(result, List)
    return result
