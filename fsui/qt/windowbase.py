from weakref import ref
from .qt import Qt, QDesktopWidget, QSignal
from .. import default_window_center, default_window_parent


_windows = set()


# noinspection PyPep8Naming
def WindowBase(BaseClass):

    # noinspection PyPep8Naming
    class WindowBaseImplementation(BaseClass):

        closed = QSignal()

        def __init__(self, parent, *args, title="", border=True, **kwargs):
            if parent is None and len(default_window_parent) > 0:
                parent = default_window_parent[-1]
                print("using default parent", parent)
                parent = parent.real_window()

            super().__init__(parent, *args, **kwargs)
            # MixinBase.__init__(self)

        # noinspection PyUnusedLocal
        # def init_window(self, parent, title):
            # self.init_mixin_base()
            self.setWindowTitle(title)

            self.layout = None
            self._size_specified = False
            self.already_closed = False
            self.close_listeners = []
            _windows.add(self)
            self.destroyed.connect(self.__destroyed)
            self.closed.connect(self.__closed)
            self._window = ref(self)
            self.setAttribute(Qt.WA_DeleteOnClose, True)
            if not border:
                self.setWindowFlags(Qt.FramelessWindowHint |
                                    Qt.NoDropShadowWindowHint)
                # self.setWindowFlags(Qt.FramelessWindowHint)
            self._centered_on_initial_show = False
            if hasattr(self, "accepted"):
                self.accepted.connect(self.__accepted)
            if hasattr(self, "rejected"):
                self.rejected.connect(self.__rejected)

        def center_on_initial_show(self):
            if self._centered_on_initial_show:
                return
            if self.layout and not self._size_specified:
                self.set_size(self.layout.get_min_size())
            self.on_resize()
            self.center_on_parent()
            self._centered_on_initial_show = True

        def __closed(self):
            print(str(self) + ".__closed")
            _windows.remove(self)

        def __destroyed(self):
            print(str(self) + ".__destroyed")

        def get_parent(self):
            return None

        def add_close_listener(self, function):
            # self.close_listeners.append(function)
            self.closed.connect(function)

        def get_window(self):
            return self

        def get_container(self):
            return self

        def set_icon(self, icon):
            self.setWindowIcon(icon.qicon())

        def set_icon_from_path(self, _):
            print("FIXME: Window.set_icon_from_path")

        def get_position(self):
            return self.pos().x(), self.pos().y()

        def set_position(self, position):
            self.move(position[0], position[1])

        def get_size(self):
            return self.width(), self.height()

        def set_size(self, size):
            self._size_specified = True
            # self.SetClientSize(size)
            # print("FIXME:\n\nDialog.set_size")
            self.resize(size[0], size[1])

        def get_title(self):
            return self.windowTitle()

        def set_title(self, title):
            self.setWindowTitle(title)

        def is_maximized(self):
            # return self.isMaximized()
            return self.windowState() == Qt.WindowMaximized
            # print("FIXME: always returning False")
            # return False

        def maximize(self, maximize=True):
            if maximize:
                self.showMaximized()
            else:
                self.setWindowState(Qt.WindowNoState)

        def minimize(self):
            self.setWindowState(Qt.WindowMinimized)

        def get_window_center(self):
            return self.x() + self.width() // 2, self.y() + self.height() // 2

        def center_on_parent(self):
            real_parent = self.parent()
            if real_parent:
                pp = real_parent.x(), real_parent.y()
                ps = real_parent.width(), real_parent.height()
                ss = self.get_size()
                self.move(pp[0] + (ps[0] - ss[0]) // 2,
                          pp[1] + (ps[1] - ss[1]) // 2)
            elif len(default_window_center) > 0:
                x, y = default_window_center[-1]
                ss = self.get_size()
                self.move(x - ss[0] // 2, y - ss[1] // 2,)

        def center_on_screen(self):
            frect = self.frameGeometry()
            frect.moveCenter(QDesktopWidget().availableGeometry().center())
            self.move(frect.topLeft())

        def set_background_color(self, color):
            p = self.palette()
            p.setColor(self.backgroundRole(), color)
            self.setPalette(p)

        # def show(self):
        #     if hasattr(self, "layout") and not self._size_specified:
        #         self.set_size(self.layout.get_min_size())
        #     #QMainWindow.show(self)
        #     print("")
        #     print("")
        #     print(" -- show --")
        #     print("")
        #     print("")
        #     # noinspection PyUnresolvedReferences
        #     super().show()

        def is_shown(self):
            return self.isVisible()

        def showEvent(self, _):
            if self.layout and not self._size_specified:
                self.set_size(self.layout.get_min_size())
            self.on_resize()

        def raise_and_activate(self):
            self.raise_()
            self.activateWindow()

        def on_close(self):
            pass

        def closeEvent(self, event):
            print(str(self) + ".closeEvent")
            event.accept()
            self.__on_close()

        def __rejected(self):
            print(str(self) + ".__rejected")
            self.__on_close()

        def __accepted(self):
            print(str(self) + ".__accepted")
            self.__on_close()

        def __on_close(self):
            print("WindowMixin.cleanup_on_close_event")
            if self.already_closed:
                print("Looks like a duplicate event, ignoring this one")
                return

            self.closed.emit()
            self.on_close()

            self.already_closed = True

        def resizeEvent(self, _):
            self.on_resize()

        def on_resize(self):
            if self.layout:
                self.layout.set_size(self.get_size())
                self.layout.update()

        def close(self):
            # keep this method override, it is here so references to
            # object.close can be connected to signals
            super().close()

    return WindowBaseImplementation
