from fsui.qt import QFileDialog
from fsui.qt.helpers import QParent

FILE = 0
FILES = 1
DIRECTORY = 2
NATIVE_DIALOGS = True


class FileDialog(QFileDialog):
    def __init__(
        self,
        parent=None,
        message="",
        directory="",
        file="",
        pattern="*.*",
        multiple=False,
        dir_mode=False,
    ):
        QFileDialog.__init__(self, QParent(parent), message)
        if directory:
            self.setDirectory(directory)
        if dir_mode:
            self.setFileMode(QFileDialog.Directory)
        if multiple:
            self.setFileMode(QFileDialog.ExistingFiles)
        # self.setWindowFlags()

    def __del__(self):
        print("FileDialog.__del__")

    def get_path(self):
        return self.get_paths()[0]

    def get_paths(self):
        return self.selectedFiles()

    def show_modal(self):
        result = self.exec_()
        print("File dialog result is", result)
        return result

    # def show(self):
    #     return self.show_modal()


def pick_directory(parent=None, message="", directory=""):
    return pick_file(
        parent=parent, message=message, directory=directory, what=DIRECTORY
    )


def pick_file(parent=None, message="", directory="", what=FILE):
    if NATIVE_DIALOGS:
        if what == DIRECTORY:
            result = QFileDialog.getExistingDirectory(
                QParent(parent), message, directory
            )
        elif what == FILES:
            # return value is filenames, selected_filter
            result = QFileDialog.getOpenFileNames(
                QParent(parent), message, directory
            )
        else:
            # return value is filename, selected_filter
            result = QFileDialog.getOpenFileName(
                QParent(parent), message, directory
            )
        if isinstance(result, tuple):
            # PySide returns a tuple, path is first param
            result = result[0]
    else:
        dialog = QFileDialog(parent, message)
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


def pick_files(parent=None, message="", directory="", what=FILE):
    return pick_file(
        parent=parent, message=message, directory=directory, what=FILES
    )
