from fsui.qt import QWidget, QVBoxLayout, QPushButton
from .desktopwidget import DesktopWidget
from .taskbarwidget import TaskBarWidget
from .titlebarwidget import TitleBarWidget


class ShellWidget(QWidget):

    def __init__(self, parent, window_handler):
        super().__init__(parent)

        self.title_bar = TitleBarWidget(self, window_handler)
        self.desktop = DesktopWidget(self)
        self.task_bar = TaskBarWidget(self, window_handler)

        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(self.title_bar)
        self.layout.addWidget(self.desktop, 1)
        self.layout.addWidget(self.task_bar)
