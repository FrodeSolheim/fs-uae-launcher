from fsui.qt import QSize, QColor, QLabel, QHBoxLayout
from fsui.qt import QMainWindow, QWidget, QVBoxLayout
from fs_uae_workspace.vfs import VFSDesktopItem

_root_window = None
_desktop_window = None


class DesktopWindow(QMainWindow):

    def __init__(self):
        QMainWindow.__init__(self)
        # .TopToBottom, self)

        self.root = QWidget(self)
        self.setCentralWidget(self.root)

        # self.root.setAutoFillBackground(True)
        # p = self.root.palette()
        # p.setColor(self.root.backgroundRole(), QColor(0xaa, 0xaa, 0xaa))
        # self.root.setPalette(p)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # self.root.setSizePolicy(QSizePolicy(2, 2), QSizePolicy(2, 2))
        # layout.addWidget(self.root, 1)
        # self.setLayout(layout)

        self.setMinimumSize(QSize(1600, 900))
        self.show()
        # self.showMaximized()

        self.top = QWidget()
        self.top.setAutoFillBackground(True)
        p = self.top.palette()
        p.setColor(self.top.backgroundRole(), QColor(0xff, 0xff, 0xff))
        self.top.setPalette(p)
        # self.top.setStyleSheet("background-color: #ffffff;")
        self.top.setMinimumHeight(26)
        layout.addWidget(self.top)

        workspace_label = QLabel("Workspace")
        top_layout = QHBoxLayout()
        top_layout.setContentsMargins(10, 0, 0, 0)
        top_layout.addWidget(workspace_label)
        self.top.setLayout(top_layout)

        # self.top_padding = QWidget()
        # self.top_padding.setAutoFillBackground(True)
        # p = self.top_padding.palette()
        # p.setColor(self.top_padding.backgroundRole(),
        #            QColor(0xaa, 0xaa, 0xaa))
        # self.top_padding.setPalette(p)
        # self.top_padding.setMinimumHeight(26)
        # layout.addWidget(self.top_padding)

        self.root_item = VFSDesktopItem()
        from fs_uae_workspace.vfsui import VFSIconView
        self.icon_view = VFSIconView(None, self.root_item)
        self.icon_view.show()
        self.icon_view.resize(20, 20)

        layout.addWidget(self.icon_view)

        self.root.setLayout(layout)

    def get_root_window(self):
        return self.root


def get_desktop_window():
    global _desktop_window
    if not _desktop_window:
        _desktop_window = DesktopWindow()
    return _desktop_window


def get_root_window():
    return get_desktop_window().get_root_window()
