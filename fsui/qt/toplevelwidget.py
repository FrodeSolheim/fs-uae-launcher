from dataclasses import dataclass
from logging import getLogger
from typing import Optional, Set, cast
from weakref import ref

from fspy.decorators import deprecated
from fsui.qt.qt import QDesktopWidget, QSignal
from fswidgets.qt.core import QEvent, QObject, Qt
from fswidgets.qt.gui import QKeyEvent
from fswidgets.qt.widgets import QWidget
from fswidgets.types import Point, Size, WindowState
from fswidgets.widget import Widget

log = getLogger(__name__)

_windows: Set["TopLevelWidget"] = set()


@dataclass
class WindowMargins:
    top: int
    right: int
    bottom: int
    left: int


class TopLevelWidget(Widget):
    # FIXME: Move more signals here?
    closed = QSignal()
    window_focus_changed = QSignal()

    # FIXME: Deprecated
    activated = QSignal()
    # FIXME: Deprecated
    deactivated = QSignal()

    def __init__(
        # FIXME: Rename escape to closeOnEscape
        self,
        parent: Optional[Widget],
        qwidget: QWidget,
        escape: bool = False,
    ):
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

        # self._windowSizeHasBeenSet = False

        self.close_listeners = []

        # self._qwidget.destroyed.connect(self.__destroyed)

        # Maybe set to True as default? As the window will likely be activated
        # when shown?
        # self.__active = False

        self.__already_closed = False
        self.__centered_on_initial_show = False

        # self.__closeOnEscape = escape

        self._nonMaximizedPosition = (0, 0)
        self._nonMaximizedSize = (0, 0)

        # Hmm, needed, document why
        self._window = ref(self)

        self.windowNormalBorders = WindowMargins(0, 0, 0, 0)
        self.windowMaximizedBorders = WindowMargins(0, 0, 0, 0)
        self.windowBorders = self.windowNormalBorders
        self.windowMargins = WindowMargins(0, 0, 0, 0)

        # Whether the widget has had its size set yet. Used by code to switch
        # to fullscreen. Also, when size is specified before showing the window,
        # we do not want to set size from layout.
        self._windowSizeHasBeenSet = False

        _windows.add(self)

    # -------------------------------------------------------------------------

    def getTitle(self) -> str:
        return self.qwidget.windowTitle()

    def __handlePositionChange(self, position: Point):
        maximized = self.isMaximized()
        if maximized:
            # self.windowBorders = self.windowMaximizedBorders
            pass
        else:
            # self.windowBorders = self.windowNormalBorders
            print("self._nonMaximizedPosition =", position)
            self._nonMaximizedPosition = position

    def __handleSizeChange(self, size: Size):
        maximized = self.isMaximized()
        if maximized:
            # self.windowBorders = self.windowMaximizedBorders
            pass
        else:
            # self.windowBorders = self.windowNormalBorders
            print("self._nonMaximizedSize =", size)
            self._nonMaximizedSize = size
        self._windowSizeHasBeenSet = True

    def isActive(self) -> bool:
        return self.qwidget.isActiveWindow()

    def isMaximized(self) -> bool:
        return self.qwidget.windowState() == Qt.WindowMaximized

    def maximize(self, maximize: bool = True):
        """The maximize parameter is deprecated."""
        self.setMaximized(maximize)

    def minimize(self):
        self.qwidget.setWindowState(Qt.WindowMinimized)

    def onClose(self):
        pass

    def raiseAndActivate(self):
        self.qwidget.raise_()
        self.qwidget.activateWindow()

    def setMaximized(self, maximized: bool):
        # if maximized:
        #     self._nonMaximizedPosition = self.getPosition()
        #     self._nonMaximizedSize = self.getSize()
        self.set_maximized(maximized)

    def setTitle(self, title: str):
        self.qwidget.setWindowTitle(title)

    # -------------------------------------------------------------------------

    def clientPositionToWindowPosition(self, position: Point):
        return (
            position[0] - self.windowBorders.left - self.windowMargins.left,
            position[1] - self.windowBorders.top - self.windowMargins.top,
        )

    def clientSizeToWindowSize(self, size: Size):
        return (
            size[0]
            + self.windowBorders.left
            + self.windowBorders.right
            + self.windowMargins.left
            + self.windowMargins.right,
            size[1]
            + self.windowBorders.top
            + self.windowBorders.bottom
            + self.windowMargins.top
            + self.windowMargins.bottom,
        )

    def windowPositionToClientPosition(self, position: Point):
        return (
            position[0] + self.windowBorders.left + self.windowMargins.left,
            position[1] + self.windowBorders.top + self.windowMargins.top,
        )

    def windowSizeToClientSize(self, size: Size):
        return (
            size[0]
            - self.windowBorders.left
            - self.windowBorders.right
            - self.windowMargins.left
            - self.windowMargins.right,
            size[1]
            - self.windowBorders.top
            - self.windowBorders.bottom
            - self.windowMargins.top
            - self.windowMargins.bottom,
        )

    def getPosition(self) -> Point:
        return self.windowPositionToClientPosition(super().getPosition())

    def getSize(self) -> Size:
        return self.windowSizeToClientSize(super().getSize())

    def setPosition(self, position: Point):
        self.__handlePositionChange(position)
        super().setPosition(self.clientPositionToWindowPosition(position))

    def setSize(self, size: Size):
        if size[0] == 0 or size[1] == 0:
            log.warning("TopLevelWidget.setSize: Ignoring size", size)
            return
        self.__handleSizeChange(size)
        # self._windowSizeHasBeenSet = True
        # self.SetClientSize(size)
        # print("FIXME:\n\nDialog.set_size")
        # super().setSize(size)
        super().setSize(self.clientSizeToWindowSize(size))

    def setPositionAndSize(self, position: Point, size: Size):
        self.__handlePositionChange(position)
        self.__handleSizeChange(size)
        super().setPositionAndSize(
            self.clientPositionToWindowPosition(position),
            self.clientSizeToWindowSize(size),
        )

    # def getClientPosition(self) -> Point:
    #     """Same as getPosition. See getWindowPosition"""
    #     return self.getPosition()

    # def getClientSize(self) -> Size:
    #     """Same as getSize, at least for now. See getWindowSize."""
    #     return self.getSize()

    # def setClientPosition(self, position: Point):
    #     """Same as setPosition, at least for now. See setWindowPosition."""
    #     self.setPosition(position)

    # def setClientSize(self, size: Size):
    #     """Same as setSize, at least for now. See setWindowSize."""
    #     self.setSize(size)

    def getWindowState(self) -> WindowState:
        """Return position, size and maximization state in a data object."""
        # pos = self.getClientPosition()
        # size = self.getClientSize()
        pos = self._nonMaximizedPosition
        size = self._nonMaximizedSize
        # pos = self.getPosition()
        # size = self.getSize()
        maximized = self.isMaximized()
        return WindowState(
            x=pos[0],
            y=pos[1],
            width=size[0],
            height=size[1],
            maximized=maximized,
        )

    def getWindowPosition(self) -> Point:
        """Return window position including window decorations."""
        return super().getPosition()

    def getWindowSize(self) -> Size:
        """Return window size including window decorations."""
        return super().getSize()

    def setWindowPosition(self, position: Point):
        """Set window position including window decorations."""
        super().setPosition(position)

    def setWindowPositionAndSize(self, position: Point, size: Size):
        """Set window position and size including window decorations."""
        super().setPositionAndSize(position, size)

    def setWindowSize(self, size: Size):
        """Set window size including window decorations."""
        super().setSize(size)

    def getUnscaledPosition(self) -> Point:
        x, y = self.getPosition()
        scale = self.qwidget.devicePixelRatioF()
        return round(x * scale), round(y * scale)

    def getUnscaledSize(self) -> Size:
        w, h = self.getSize()
        scale = self.qwidget.devicePixelRatioF()
        return round(w * scale), round(h * scale)

    def getUnscaledWindowPosition(self) -> Point:
        x, y = self.getWindowPosition()
        scale = self.qwidget.devicePixelRatioF()
        return round(x * scale), round(y * scale)

    def getUnscaledWindowSize(self) -> Size:
        w, h = self.getWindowSize()
        scale = self.qwidget.devicePixelRatioF()
        return round(w * scale), round(h * scale)

    def restoreDefaultSize(self):
        """Can be implemented by subclasses."""
        pass

    # -------------------------------------------------------------------------

    def on_resize(self):

        # maximized = self.isMaximized()
        # if maximized:
        #     self.windowBorders = self.windowMaximizedBorders
        # else:
        #     self.windowBorders = self.windowNormalBorders

        # self.contentMargins.top = self.windowBorders.top + self.windowMargins.top
        # self.contentMargins.right = self.windowBorders.right + self.windowMargins.right
        # self.contentMargins.bottom = self.windowBorders.bottom + self.windowMargins.bottom
        # self.contentMargins.left = self.windowBorders.left + self.windowMargins.left
        super().on_resize()

    # FIXME: REMOVE? close signal instead
    def add_close_listener(self, function):
        # self.close_listeners.append(function)
        self.closed.connect(function)

    def center_on_initial_show(self):
        if self.__centered_on_initial_show:
            return
        if self.layout and not self._windowSizeHasBeenSet:
            self.set_size(self.layout.get_min_size())
        self.on_resize()
        self.center_on_parent()
        self.__centered_on_initial_show = True

    def center_on_parent(self):
        print("TopLevelWidget.center_on_parent")
        self.set_initial_size_from_layout()
        print("parent", self.parent())
        print("qwidget:", self._qwidget)
        real_parent = self._qwidget.parent()
        print("center_on_parent real_parent = ", real_parent)
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

    def center_on_window(self, other):
        print(f"TopLevelWidget.center_on_window other={other}")
        self.set_initial_size_from_layout()
        # print("parent", self.parent())
        # print("qwidget:", self._qwidget)
        # real_parent = other._qwidget.parent()
        # print("center_on_parent real_parent = ", real_parent)
        # if real_parent:
        # pp = other.x(), other.y()
        # ps = other.width(), other.height()
        pp = other.position()
        ps = other.size()
        ss = self.size()
        print(pp, ps, ss)
        self.set_position(
            (pp[0] + (ps[0] - ss[0]) // 2, pp[1] + (ps[1] - ss[1]) // 2)
        )

    def center_on_screen(self):
        frame_rect = self._qwidget.frameGeometry()
        frame_rect.moveCenter(QDesktopWidget().availableGeometry().center())
        self._qwidget.move(frame_rect.topLeft())

    def close(self):
        self._qwidget.close()

    # def __destroyed(self):
    #     print(f"TopLevelWidget.__destroyed self={self}")

    def eventFilter(self, a0: QObject, a1: QEvent):
        obj = a0
        event = a1
        eventType = event.type()
        if eventType == QEvent.Close:
            assert obj == self._qwidget
            # print(f"DialogWrapper.closeEvent self={self})")
            # super().closeEvent(event)
            # self._fswidget.on_close()
            if self.__already_closed:
                print("Looks like a duplicate event, ignoring this one")
            else:
                self.__already_closed = True
                _windows.remove(self)
                self.onClose()
                self.on_close()
        elif eventType == QEvent.KeyPress:
            keyEvent = cast(QKeyEvent, event)
            if keyEvent.key() == Qt.Key_Escape:
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
        return self.isMaximized()

    @deprecated
    def maximized(self):
        return self.isMaximized()

    def on_close(self):
        self.closed.emit()

    def onWindowFocusChanged(self):
        """Overrides the base function and emits a signal by default.

        Only top-level widgets does this. Normal widgets only have the
        onWindowFocusChanged method."""
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

    @deprecated
    def raise_and_activate(self):
        self.raiseAndActivate()

    def set_icon(self, icon):
        self.qwidget.setWindowIcon(icon.qicon())

    def set_icon_from_path(self, _):
        print("FIXME: Window.set_icon_from_path")

    def set_initial_size_from_layout(self):
        if self.layout and not self._windowSizeHasBeenSet:
            self.set_size_from_layout()

    @deprecated
    def set_maximized(self, maximize: bool = True, geometry=None):

        if maximize:
            self.windowBorders = self.windowMaximizedBorders
        else:
            self.windowBorders = self.windowNormalBorders


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
            self.qwidget.showMaximized()
            print("size after showMaximized", self.getSize())
        else:
            # self.restore_margins()
            self.qwidget.setWindowState(Qt.WindowNoState)

    def set_size_from_layout(self):
        size = self.layout.get_min_size()
        print(f"set_size_from_layout, size = {size}")
        self.setSize(size)

    @deprecated
    def title(self):
        return self.getTitle()

    @deprecated
    def set_title(self, title: str):
        self.setTitle(title)

    @deprecated
    def unscaled_position(self):
        return self.getUnscaledWindowPosition()

    @deprecated
    def unscaled_size(self):
        return self.getUnscaledWindowSize()

    # def show(self):
    #     if hasattr(self, "layout") and not self._windowSizeHasBeenSet:
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

    #     if self.layout and not self._windowSizeHasBeenSet:
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
