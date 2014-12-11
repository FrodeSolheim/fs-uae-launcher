try:
    from Xlib.display import Display
except ImportError:
    Display = None


def configure_dock_window(widget, left, right, top, bottom):
    xid = widget.winId()
    # convert to int in case it is a sip.voidptr object (pyqt5)
    xid = int(xid)
    display = Display()
    window = display.create_resource_object("window", xid)
    # _NET_WM_DESKTOP = display.intern_atom("_NET_WM_DESKTOP")
    _NET_WM_STRUT = display.intern_atom("_NET_WM_STRUT")
    _NET_WM_STATE = display.intern_atom("_NET_WM_STATE")
    # noinspection PyPep8Naming
    ATOM = display.intern_atom("ATOM")
    # _NET_WM_STATE_SKIP_TASKBAR = display.intern_atom(
    #     "_NET_WM_STATE_SKIP_TASKBAR")
    # _NET_WM_STATE_SKIP_PAGER = display.intern_atom(
    #     "_NET_WM_STATE_SKIP_PAGER")
    _NET_WM_STATE_BELOW = display.intern_atom(
        "_NET_WM_STATE_BELOW")
    # _NET_WM_USER_TIME = display.intern_atom(
    #     "_NET_WM_USER_TIME")
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
        _NET_WM_STRUT, CARDINAL, 32, [left, right, top, bottom])

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
