from weakref import ref

from fspy.decorators import deprecated
from fsui.qt.qt import Qt, QDesktopWidget, QSignal, QEvent
from fsui.qt.widget import Widget

_windows = set()


class TopLevelWidget(Widget):
    # FIXME: Move more signals here?
    closed = QSignal()
    window_focus_changed = QSignal()

    # FIXME: Deprecated
    activated = QSignal()
    # FIXME: Deprecated
    deactivated = QSignal()

    def __init__(self, parent, qwidget, escape=False):
        super().__init__(parent, qwidget)

        # self._qwidget = qwidget
        # if parent is None and len(default_window_parent) > 0:
        #     parent = default_window_parent[-1]
        #     print("using default parent", parent)
        #     parent = parent.real_window()
        # super().__init__(parent, *args, **kwargs)
        # MixinBase.__init__(self)

        # noinspection PyUnusedLocal
        # def init_window(self, parent, title):
        # self.init_mixin_base()
        # self.setWindowTitle(title)

        self.layout = None

        # When size is specified before showing the window, we do not want to
        # set size from layout.
        self._size_specified = False

        self.close_listeners = []

        # self._qwidget.destroyed.connect(self.__destroyed)

        # Maybe set to True as default? As the window will likely be activated
        # when shown?
        self.__active = False
        self.__already_closed = False
        self.__centered_on_initial_show = False
        self.__close_on_escape = escape

        # Hmm, needed, document why
        self._window = ref(self)

        _windows.add(self)

    # FIXME: REMOVE? close signal instead
    def add_close_listener(self, function):
        # self.close_listeners.append(function)
        self.closed.connect(function)

    def center_on_initial_show(self):
        if self.__centered_on_initial_show:
            return
        if self.layout and not self._size_specified:
            self.set_size(self.layout.get_min_size())
        self.on_resize()
        self.center_on_parent()
        self.__centered_on_initial_show = True

    def center_on_parent(self):
        self.set_initial_size_from_layout()
        real_parent = self._qwidget.parent()
        # print("center_on_parent real_parent = ",
        #       real_parent, default_window_center)
        if real_parent:
            pp = real_parent.x(), real_parent.y()
            ps = real_parent.width(), real_parent.height()
            ss = self.size()
            print(pp, ps, ss)
            self.set_position(
                (pp[0] + (ps[0] - ss[0]) // 2, pp[1] + (ps[1] - ss[1]) // 2)
            )
        # elif len(default_window_center) > 0:
        #     x, y = default_window_center[-1]
        #     ss = self.size()
        #     self.set_position((x - ss[0] // 2, y - ss[1] // 2))

        # # FIXME: ?
        # real_parent = self.parent()
        # if real_parent:
        #     pp = real_parent.x(), real_parent.y()
        #     ps = real_parent.width(), real_parent.height()
        #     ss = self.get_size()
        #     self.set_position(
        #         (pp[0] + (ps[0] - ss[0]) // 2, pp[1] + (ps[1] - ss[1]) // 2)
        #     )
        # # elif len(default_window_center) > 0:
        # #     x, y = default_window_center[-1]
        # #     ss = self.get_size()
        # #     self.move(x - ss[0] // 2, y - ss[1] // 2,)

    def center_on_screen(self):
        frame_rect = self._qwidget.frameGeometry()
        frame_rect.moveCenter(QDesktopWidget().availableGeometry().center())
        self._qwidget.move(frame_rect.topLeft())

    def close(self):
        self._qwidget.close()

    # def __destroyed(self):
    #     print(f"TopLevelWidget.__destroyed self={self}")

    def eventFilter(self, obj, event):
        event_type = event.type()
        if event_type == QEvent.Close:
            assert obj == self._qwidget
            # print(f"DialogWrapper.closeEvent self={self})")
            # super().closeEvent(event)
            # self._fswidget.on_close()
            if self.__already_closed:
                print("Looks like a duplicate event, ignoring this one")
            else:
                self.__already_closed = True
                _windows.remove(self)
                self.on_close()
        elif event_type == QEvent.KeyPress:
            if event.key() == Qt.Key_Escape:
                if hasattr(self, "end_modal"):
                    self.end_modal(False)
                self.close()
                return True
        return super().eventFilter(obj, event)

    # def closeEvent(self, event):
    #     print(f"DialogWrapper.closeEvent self={self})")
    #     super().closeEvent(event)
    #     self._fswidget.on_close()

    #     if event_type == QEvent.WindowActivate:
    #         # FIXME: It seems that if we let this even pass on to further
    #         # processing, we end up with a lot of activation events, slowing
    #         # things down. Why?
    #         # Ah, all widgets in the widget hierarchy gets an activate event,
    #         # and it probably (?) bubbles up to the window...
    #         # FIXME: Consider renaming activated (conflicts with e.g. button)
    #         # and expose (window) activated events to widget hierarchy.
    #         # e.g window_activated / window_deactivated /
    #         # "window_activation_changed" (can check ._window_active())
    #         # window_focus_changed
    #         if obj == self._qwidget:
    #             # print("activateEvent", obj)
    #             if not self.__active:
    #                 self.__active = True
    #                 self.activated.emit()
    #     elif event_type == QEvent.WindowDeactivate:
    #         if obj == self._qwidget:
    #             # print("deactivateEvent", obj)
    #             if self.__active:
    #                 self.__active = False
    #                 self.deactivated.emit()
    #     return super().eventFilter(obj, event)

    @deprecated
    def get_container(self):
        return self

    @deprecated
    def get_parent(self):
        return self.parent()

    @deprecated
    def get_title(self):
        return self.title()

    @deprecated
    def get_window(self):
        return self

    @deprecated
    def get_window_center(self):
        # qobj = self._qwidget
        # return qobj.x() + qobj.width() // 2, qobj.y() + qobj.height() // 2
        position = self.position()
        size = self.size()
        return position[0] + size[0] // 2, position[1] + size[1] // 2

    @deprecated
    def is_maximized(self):
        return self.maximized()

    def maximize(self, maximize=True):
        if maximize:
            self._qwidget.showMaximized()
        else:
            self._qwidget.setWindowState(Qt.WindowNoState)

    def maximized(self):
        # return self.isMaximized()
        return self._qwidget.windowState() == Qt.WindowMaximized
        # print("FIXME: always returning False")
        # return False

    def minimize(self):
        # self.setWindowState(Qt.WindowMinimized)
        # return self._real_window.minimize()
        self._qwidget.setWindowState(Qt.WindowMinimized)

    def on_close(self):
        self.closed.emit()

    def on_window_focus_changed(self):
        """Overrides the base function and emits a signal by default.
        
        Only top-level widgets does this. Normal widgets only have the
        on_window_focus_changed method."""
        # print("TopLevelWindow.window_focus_changed")
        self.window_focus_changed.emit()
        # FIXME: Deprecated signals
        if self.window_focus():
            # print("Emitting activated signal")
            self.activated.emit()
        else:
            self.deactivated.emit()

    # Widget
    # def on_resize(self):
    #     print(f"TopLevelWidget.on_resize self={self}")
    #     if self.layout:
    #         self.layout.set_size(self.get_size())
    #         self.layout.update()

    # def position(self):
    #     pos = self._qwidget.pos()
    #     return pos.x(), pos.y()

    def raise_and_activate(self):
        self._qwidget.raise_()
        self._qwidget.activateWindow()

    def set_icon(self, icon):
        self.setWindowIcon(icon.qicon())

    def set_icon_from_path(self, _):
        print("FIXME: Window.set_icon_from_path")

    def set_initial_size_from_layout(self):
        if self.layout and not self._size_specified:
            self.set_size_from_layout()

    def set_maximized(self, maximize=True, geometry=None):
        # We must set the size before maximizing, so this isn't done within
        # showMaximized -> ... -> set_initial_size_from_layout -> set_size.
        self.set_initial_size_from_layout()
        # self._qwidget.set_maximized(maximize, geometry)

        print("set_maximized", maximize)
        if maximize:
            # self.margins.set(0)
            # if geometry is not None:
            #     print("set_maximized geometry", geometry)
            #     self.setGeometry(*geometry)
            # else:
            #     if not self._size_set:
            #         self._size_set = True
            #         print("resizing to 1, 1")
            #         self.resize(1, 1)
            # self.resize(1, 1)
            # self.resize(1920, 1080)
            self._qwidget.showMaximized()
            print("size after showMaximized", self.size())
        else:
            # self.restore_margins()
            self._qwidget.setWindowState(Qt.WindowNoState)

    def set_size(self, size):
        self._size_specified = True
        # self.SetClientSize(size)
        # print("FIXME:\n\nDialog.set_size")
        if size[0] == 0 or size[1] == 0:
            print("TopLevelWidget.set_size ignoring size", size)
            return
        super().set_size(size)

    def set_size_from_layout(self):
        size = self.layout.get_min_size()
        print(f"set_size_from_layout, size = {size}")
        self.set_size(size)

    def title(self):
        return self._qwidget.windowTitle()

    def set_title(self, title):
        self._qwidget.setWindowTitle(title)

    def unscaled_position(self):
        x, y = self.position()
        scale = self._qwidget.devicePixelRatioF()
        return round(x * scale), round(y * scale)

    def unscaled_size(self):
        w, h = self.size()
        scale = self._qwidget.devicePixelRatioF()
        return round(w * scale), round(h * scale)

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

    # def showEvent(self, _):
    #     # FIXME
    #     # FIXME
    #     # FIXME

    #     if self.layout and not self._size_specified:
    #         self.set_size(self.layout.get_min_size())
    #     self.on_resize()

    # FIXME:::
    # def closeEvent(self, event):
    #     print(str(self) + ".closeEvent")
    #     event.accept()
    #     self.__on_close()

    # FIXME:::
    # def __rejected(self):
    #     print(str(self) + ".__rejected")
    #     self.__on_close()

    # def __accepted(self):
    #     print(str(self) + ".__accepted")
    #     self.__on_close()

    # FIXME:
    # def resizeEvent(self, _):
    #     self.on_resize()
