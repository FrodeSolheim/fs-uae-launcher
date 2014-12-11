from fsui.qt import QSignal, QObject, QX11Info
# print("a")
# try:
#     # noinspection PyUnresolvedReferences
#     from gi.repository import Gdk
# except ImportError:
#     Gdk = None
# print("b")
try:
    # noinspection PyUnresolvedReferences
    from gi import require_version
    require_version("Wnck", "1.0")
    from gi.repository import Wnck

    # require_version("Gtk", "2.0")
    # from gi.repository import Gtk

    # Wnck.enable_wnck(version="1.0")
    # print(dir(Wnck))
except ImportError:
    Wnck = None
print("c")


class WindowProxy:

    def __init__(self, window, changed=""):
        self.window = window
        self.changed = changed

    @property
    def name(self):
        if self.window is None:
            return ""
        return self.window.get_name()

    def activate(self):
        if self.window is None:
            return
        if self.window.is_active():
            self.window.minimize()
            return
        #self.window.activate(time.time())
        # noinspection PyArgumentList
        self.window.activate(QX11Info.appTime())

    def is_active(self):
        if self.window is None:
            return False
        return self.window.is_active()

    def is_minimized(self):
        if self.window is None:
            return False
        return self.window.is_minimized()

    def is_desktop(self):
        if self.window is None:
            return False
        return self.window.get_window_type() == Wnck.WindowType.DESKTOP

    def open_menu(self, bottom_left):
        # menu = Wnck.ActionMenu.new(self.window)
        # print(menu)
        # #Gtk.Menu.menu_popup(menu)
        # print(dir(menu))
        # menu.menu_popup()
        pass

    def __eq__(self, other):
        return self.window == other.window


class RealWindowHandler(QObject):

    window_added = QSignal(WindowProxy)
    window_removed = QSignal(WindowProxy)
    window_activated = QSignal(WindowProxy)
    window_changed = QSignal(WindowProxy)

    def __init__(self):
        QObject.__init__(self)
        if Wnck is None:
            return
        self.screen = Wnck.Screen.get_default()
        # self.screen.force_update()
        print(self.screen)
        self.screen.connect("window-opened", self.__window_opened)
        self.screen.connect("window-closed", self.__window_closed)
        self.screen.connect("active-workspace-changed",
                            self.__active_workspace_changed)
        self.screen.connect("active-window-changed",
                            self.__active_window_changed)

        self.workspace_index = 0
        self.workspace = None
        # workspace = self.screen.get_workspace()
        # self.workspace_index = self.screen.get_workspace()
        self.all_windows = []
        self.workspace_windows = []
        self.active_window = None

    def __active_window_changed(self, screen, old_window):
        print("__active_window_changed", old_window)
        if screen != self.screen:
            return
        self.active_window = screen.get_active_window()
        print("emit", self.active_window)
        self.window_activated.emit(WindowProxy(self.active_window))
        self.window_changed.emit(WindowProxy(old_window, "active"))
        self.window_changed.emit(WindowProxy(self.active_window, "active"))

    def __window_opened(self, screen, window):
        if screen != self.screen:
            return
        print(screen, window)
        self.all_windows.append(window)
        if self.is_window_relevant(window):
            self.add_workspace_window(window)

    def __window_closed(self, screen, window):
        if screen != self.screen:
            return
        if window in self.workspace_windows:
            self.remove_workspace_window(window)
        self.all_windows.remove(window)

    def is_window_relevant(self, window):
        if window.is_skip_tasklist():
            return False
        workspace = window.get_workspace()
        if workspace is not None and workspace != self.workspace:
            return False
        #    # pinned to all workspaces
        #    return True
        #if workspace.get_number() != self.workspace_index:
        #    return False
        #if workspace != self.workspace:
        #    return False
        return True

    def add_workspace_window(self, window):
        print("- add", window)
        print(" ", window.get_name())
        self.workspace_windows.append(window)

        window.connect("state-changed", self.__window_state_changed)
        window.connect("name-changed", self.__window_name_changed)

        print("emitting window added signal")
        self.window_added.emit(WindowProxy(window))

    def remove_workspace_window(self, window):
        print("- remove", window)
        # window.disconnect(self.__window_state_changed)
        self.workspace_windows.remove(window)
        self.window_removed.emit(WindowProxy(window))

    def __window_state_changed(self, window, changed_mask, new_state):
        self.window_changed.emit(WindowProxy(window, "state"))

    def __window_name_changed(self, window):
        print("__window_name_changed", window)
        self.window_changed.emit(WindowProxy(window, "name"))

    def __active_workspace_changed(self, screen, previous_workspace):
        if screen != self.screen:
            return
        print("new workspace", screen, previous_workspace)
        self.workspace = self.screen.get_active_workspace()
        self.workspace_index = self.workspace.get_number()

        print("workspace index is", self.workspace_index)
        add_windows = []
        remove_windows = []
        for window in self.all_windows:
            if self.is_window_relevant(window):
                if window not in self.workspace_windows:
                    add_windows.append(window)
            else:
                if window in self.workspace_windows:
                    remove_windows.append(window)

        for window in remove_windows:
            self.remove_workspace_window(window)
        for window in add_windows:
            self.add_workspace_window(window)
