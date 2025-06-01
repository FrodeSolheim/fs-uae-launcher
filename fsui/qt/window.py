import weakref
from typing import Any, Optional, Tuple, cast

from PyQt6.QtGui import QMoveEvent, QResizeEvent, QShowEvent

from fscore.deprecated import deprecated
from fscore.system import System
from fsui.qt.color import Color
from fsui.qt.icon import Icon
from fsui.qt.qparent import QOptionalParent
from fsui.qt.qt import QMainWindow, Qt, init_qt
from fsui.qt.toplevelwidget import TopLevelWidget
from fsui.qt.widgets import QWidget
from fswidgets.types import Point
from fswidgets.widget import Widget


class WindowWrapper(QMainWindow):
    def __init__(
        self,
        parent: Optional[Widget],
        # child,
        *,
        below: bool = False,
        border: bool = True,
        fswidget: Widget,
        minimizable: bool = True,
        maximizable: bool = True,
        title: str,
    ) -> None:
        print(f"\nWindowWrapper.__init__ parent={parent}")
        super().__init__(QOptionalParent(parent, window=True))
        # self.margins = Margins()
        self.setWindowTitle(title)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        flags: int = Qt.WindowType.Window
        if System.macos:
            flags &= ~Qt.WindowType.WindowFullscreenButtonHint

        if border:
            flags |= Qt.WindowType.CustomizeWindowHint
            flags |= Qt.WindowType.WindowCloseButtonHint
            flags |= Qt.WindowType.WindowTitleHint
            if minimizable:
                flags |= Qt.WindowType.WindowMinimizeButtonHint
            if maximizable:
                flags |= Qt.WindowType.WindowMaximizeButtonHint
            # else:
            #     flags &= ~Qt.WindowType.WindowMaximizeButtonHint
        else:
            flags |= Qt.WindowType.FramelessWindowHint
            # flags |= Qt.NoDropShadowWindowHint
            if below:
                flags |= Qt.WindowType.WindowStaysOnBottomHint
        self.setWindowFlags(flags)
        # self.setAttribute(Qt.WA_DeleteOnClose, True)

        # self._child = weakref.ref(child)
        # self._child = child
        # self._fake_window = child
        # self.__already_closed = False

        # self.destroyed.connect(self.__on_destroyed)

        # Maybe...
        self._fswidget_ref = weakref.ref(fswidget)

    # # FIXME: Move to BaseWindow / eventFilter?
    # def closeEvent(self, event):
    #     print(f"DialogWrapper.closeEvent self={self})")
    #     super().closeEvent(event)
    #     self._fswidget.on_close()

    @property
    def _fswidget(self) -> Widget:
        widget = self._fswidget_ref()
        assert widget
        return widget

    def resizeEvent(self, a0: QResizeEvent) -> None:
        self._fswidget.on_resize()

    def moveEvent(self, a0: QMoveEvent) -> None:
        # print("onShow (move)", self.x(), self.y())
        self._fswidget.onMove()

    def showEvent(self, a0: QShowEvent) -> None:
        # if self.owner().center_on_show:
        #     if not self._centered_on_initial_show:
        #         if self.parent():
        #             self.owner().center_on_parent()
        #         self._centered_on_initial_show = True
        #
        # self._fswidget.set_initial_size_from_layout()
        # self._fswidget.on_resize()
        print("showEvent, onShow", self.x(), self.y())
        self._fswidget.onShow()


# noinspection PyPep8Naming
class Window(TopLevelWidget):

    # shown = QSignal()

    def __init__(
        self,
        parent: Optional[Widget] = None,
        title: str = "",
        border: bool = True,
        minimizable: bool = True,
        maximizable: bool = True,
        separator: bool = True,
        menu: bool = False,
        header: bool = True,
        below: bool = False,
        closable: bool = True,
        color: Optional[Color] = None,
        escape: bool = False,
        **_: Any,
    ):
        # FIXME: More like this? Or init once at startup?
        init_qt()
        qwidget = WindowWrapper(
            parent,
            below=below,
            border=border,
            fswidget=self,
            minimizable=minimizable,
            maximizable=maximizable,
            title=title,
        )
        super().__init__(
            parent, qwidget, escape=escape, maximizable=maximizable
        )

        # if parent is None and len(default_window_parent) > 0:
        #     parent = default_window_parent[-1]
        #     print("using default parent", parent)

        # FIXME
        self._window = weakref.ref(self)

        # FIXME: Send via constructors?
        self.set_title(title)

        self.layout = None

        self._windowSizeHasBeenSet = False

        self.close_listeners = []
        # self.destroyed.connect(self.__destroyed)

        # self._real_window.setAttribute(Qt.WA_DeleteOnClose, True)

        # if not border:
        #     self.setWindowFlags(Qt.FramelessWindowHint |
        #                         Qt.NoDropShadowWindowHint)
        #     # self.setWindowFlags(Qt.FramelessWindowHint)

        self.center_on_show = True
        self._centered_on_initial_show = False

        # FIXME: Move to dialog?
        if hasattr(self, "accepted"):
            self.accepted.connect(self.__accepted)
        if hasattr(self, "rejected"):
            self.rejected.connect(self.__rejected)

        # self.windowBorders = WindowMargins(1, 1, 1, 1)
        # self.set_background_color(Color(0xff, 0x00, 00))

        # self.windowMargins.left = 40
        # self.windowMargins.right = 20
        # self.windowMargins.top = 10
        # self.windowMargins.bottom = 5

    # -------------------------------------------------------------------------

    # def setSize(self, size: Size):
    #     self.__handleSizeChange(size)
    #     super().setSize(size)

    # def setPositionAndSize(self, position: Point, size: Size):
    #     self.__handleSizeChange(size)
    #     super().setPositionAndSize(position, size)

    # def on_resize(self):
    #     x = self.windowBorders.left + self.windowMargins.left
    #     y = self.windowBorders.top + self.windowMargins.top
    #     width, height = self.getSize()
    #     # Margins are already account for in getSize
    #     # width -= self.windowMargins.left + self.windowMargins.right
    #     # height -= self.windowMargins.top + self.windowMargins.bottom
    #     print(x, y, width, height)
    #     self.qcontainer.setGeometry(x, y, width, height)
    #     super().on_resize()

    # -------------------------------------------------------------------------

    def alert(self, msecs: int = 0) -> None:
        init_qt().alert(self._real_window, msecs)

    def fullscreen(self) -> bool:
        return self.qMainWindow.isFullScreen()

    @deprecated
    def get_position(self) -> Point:
        return self.position()

    @deprecated
    def get_title(self) -> str:
        return self.title()

    @deprecated
    def get_window(self) -> TopLevelWidget:
        return self.top_level()

    @deprecated
    def is_fullscreen(self) -> bool:
        return self.fullscreen()

    # def add_close_listener(self, function):
    #     # self.close_listeners.append(function)
    #     self.closed.connect(function)

    def offset_from_parent(self, offset: Tuple[int, int]) -> None:
        self.set_initial_size_from_layout()
        real_parent = self.qMainWindow.parent()
        # print("offset_from_parent real_parent = ",
        #       real_parent, default_window_center)
        if real_parent:
            pp = real_parent.x(), real_parent.y()
            self.set_position((pp[0] + offset[0], pp[1] + offset[1]))

    @property
    def qMainWindow(self) -> QMainWindow:
        w = self._qwidget
        assert w is not None
        return cast(QMainWindow, w)

    # FIXME: Remove?
    def real_widget(self) -> QWidget:
        w = self._qwidget
        assert w is not None
        return w

    # FIXME: Correct?
    def real_window(self) -> QMainWindow:
        return cast(QMainWindow, self._qwidget)

    @deprecated
    def resize(self, width: int, height: int) -> None:
        self.set_size((width, height))

    def set_icon(self, icon: Icon) -> None:
        self.qMainWindow.setWindowIcon(icon.qicon())

    @deprecated
    def set_icon_from_path(self, _: str) -> None:
        print("FIXME: Window.set_icon_from_path")

    def set_fullscreen(
        self,
        fullscreen: bool = True,
        geometry: Optional[Tuple[int, int, int, int]] = None,
    ) -> None:
        # We must set the size before maximizing, so this isn't done within
        # showMaximized -> ... -> set_initial_size_from_layout -> set_size.
        self.set_initial_size_from_layout()
        # if self.title_panel is not None:
        #     self.title_panel.set_visible(not fullscreen)
        #     self.title_panel_visible = not fullscreen
        # self._qwidget.setFullscreen(fullscreen, geometry)

        if fullscreen:
            # self.margins.set(0)
            # Workaround, without setting size to something initially,
            # showFullScreen sometimes fails to update size on Linux, causing
            # only a small part of the screen to be filled.
            if geometry is not None:
                print("set_fullscreen geometry", geometry)
                self.qMainWindow.setGeometry(*geometry)
            else:
                if not self._windowSizeHasBeenSet:
                    self._windowSizeHasBeenSet = True
                    print("resizing to 1, 1")
                    self.set_size((1, 1))
            self.qMainWindow.showFullScreen()
            print("size after showFullScreen", (self.size()))
        else:
            self.restore_margins()
            self.setWindowState(Qt.WindowState.WindowNoState)

    def show(
        self,
        maximized: bool = False,
        center: bool = False,
        offset: bool = False,
    ) -> None:
        if center:
            print("CENTER")
            self.center_on_parent()
            # self._centered_on_initial_show = True
        elif offset:
            self.offset_from_parent((20, 20))
            # self._centered_on_initial_show = True
            self.center_on_show = False
        if maximized:
            self.qMainWindow.showMaximized()
        else:
            self.qMainWindow.show()

    @deprecated
    def top_level(self) -> TopLevelWidget:
        return self

    # FIXME: Don't want as property
    @property
    def window(self) -> TopLevelWidget:
        return self
