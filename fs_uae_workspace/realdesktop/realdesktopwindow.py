from fsui.qt import Qt, QDesktopWidget, QMainWindow, QDialog, QWidget
try:
    from Xlib import X
    from Xlib.display import Display
    from Xlib.error import BadAccess
    from Xlib.protocol.request import InternAtom
except ImportError:
    X = None
    Display = None
    BadAccess = None
    InternAtom = None


class RealDesktopWindow(QMainWindow):

    def __init__(self):
        # self.widget = QWidget()
        self.widget = None
        # flags = 0
        # flags |= Qt.FramelessWindowHint
        # flags |= Qt.Desktop
        # flags |= Qt.WindowStaysOnBottomHint
        # flags |= Qt.CustomizeWindowHint
        # flags |= Qt.WindowCloseButtonHint
        # flags |= Qt.WindowMinimizeButtonHint
        # flags |= Qt.Tool
        # flags |= Qt.WindowDoesNotAcceptFocus
        super().__init__(self.widget)
        self.setWindowTitle("FS-UAE Workspace")
        g = QDesktopWidget().screenGeometry()
        self.setFixedSize(g.width(), g.height())
        self.move(0, 0)

        # self.setFocusPolicy(Qt.NoFocus)
        # self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.set_x11_properties()

    def set_x11_properties(self):
        xid = self.winId()
        display = Display()
        window = display.create_resource_object("window", xid)
        _NET_WM_DESKTOP = display.intern_atom("_NET_WM_DESKTOP")
        _NET_WM_STRUT = display.intern_atom("_NET_WM_STRUT")
        _NET_WM_STATE = display.intern_atom("_NET_WM_STATE")
        ATOM = display.intern_atom("ATOM")
        _NET_WM_STATE_SKIP_TASKBAR = display.intern_atom(
            "_NET_WM_STATE_SKIP_TASKBAR")
        _NET_WM_STATE_SKIP_PAGER = display.intern_atom(
            "_NET_WM_STATE_SKIP_PAGER")
        _NET_WM_STATE_BELOW = display.intern_atom(
            "_NET_WM_STATE_BELOW")
        _NET_WM_USER_TIME = display.intern_atom(
            "_NET_WM_USER_TIME")
        _NET_WM_WINDOW_TYPE = display.intern_atom(
            "_NET_WM_WINDOW_TYPE")
        _NET_WM_WINDOW_TYPE_DOCK = display.intern_atom(
            "_NET_WM_WINDOW_TYPE_DOCK")
        # noinspection PyPep8Naming
        CARDINAL = display.intern_atom("CARDINAL")

        # Set window type to dock (skip task bar, no focus, on all desktops)
        window.change_property(
            _NET_WM_WINDOW_TYPE, ATOM, 32, [_NET_WM_WINDOW_TYPE_DOCK])
        # Reserve space for title bar and task bar
        window.change_property(
            _NET_WM_STRUT, CARDINAL, 32, [0, 0, 28, 28])

        # Show on all workspaces
        # window.change_property(
        #     _NET_WM_DESKTOP, CARDINAL, 32, [0xffffffff, 0, 0, 0])
        # Don't focus the window on window creation
        # window.change_property(
        #     _NET_WM_USER_TIME, CARDINAL, 32, [0, 0, 0, 0])
        # Don't show in task bar or window switcher
        # window.change_property(
        #     _NET_WM_STATE, ATOM, 32,
        #     [_NET_WM_STATE_SKIP_TASKBAR, _NET_WM_STATE_SKIP_PAGER])

        #
        window.change_property(_NET_WM_STATE, ATOM, 32, [_NET_WM_STATE_BELOW])


        display.sync()

    def set_shell_widget(self, shell_widget):
        self.setCentralWidget(shell_widget)
