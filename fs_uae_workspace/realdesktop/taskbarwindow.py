from fsui.qt import QDesktopWidget, QMainWindow
from .x11 import configure_dock_window


class TaskBarWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("FS-UAE Workspace Title Bar")
        g = QDesktopWidget().screenGeometry()
        self.setFixedSize(g.width(), 28)
        self.move(0, g.height() - 28)
        configure_dock_window(self, 0, 0, 0, 28)

        self.setStyleSheet("""
            background-color: #000000;
        """)
