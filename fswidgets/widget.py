from dataclasses import dataclass
from typing import Any, Callable, Optional, TypeVar, Union, cast
from weakref import ReferenceType, ref

from typing_extensions import Literal

from fscore.deprecated import deprecated
from fscore.events import Event, EventHelper, EventListener
from fscore.tasks import AsyncSingleTaskRunner, Task
from fscore.types import SimpleCallable
from fsui.qt.color import Color
from fsui.qt.font import Font
from fsui.qt.menu import PopupMenu
from fsui.qt.mouse import get_mouse_position
from fsui.qt.signal import Signal

# from fsui.qt.toplevelwidget import TopLevelWidget
from fswidgets.exceptions import NoParentError
from fswidgets.overrides import overrides
from fswidgets.qt.core import QEvent, QObject, QPoint, Qt, QTimerEvent
from fswidgets.qt.gui import QPalette
from fswidgets.qt.widgets import QWidget
from fswidgets.style import Style
from fswidgets.types import Point, Size

T = TypeVar("T")
TEvent = TypeVar("TEvent", bound=Event)


@dataclass
class ContentMargins:
    top: int
    right: int
    bottom: int
    left: int


class Widget(QObject):
    """Base class for all GUI widgets, including windows and dialogs."""

    # FIXME: Consider renaming to destroy, since the signal is sent before
    # the object is deleted and children are destroyed
    destroyed: Any = Signal()
    # FIXME: Only toplevel need to have a signal and sent out notifications
    # window_focus_changed = Signal()
    shown: Any = Signal()

    resized: Any = Signal()

    def __init__(self, parent: "Optional[Widget]", qwidget: QWidget) -> None:
        super().__init__()
        # self._widget = widget
        # self.__qwidget = ref(widget)  # ??
        self.__qwidget: Optional[QWidget] = None
        if qwidget is not None:
            self.setQWidget(qwidget)

        # from fsui.qt.window import Window
        from fsui.qt.toplevelwidget import TopLevelWidget

        self._window: Optional[ReferenceType[TopLevelWidget]] = None

        if parent is not None:
            self._parent: Any = ref(parent)
            # noinspection PyProtectedMember
            self._window = parent._window
        else:
            self._parent: Any = None

        if qwidget is not None and parent is not None:
            # FIXME: Remove?
            self.getParent().onQWidgetChildAdded(qwidget)
        if parent is not None:
            self.getParent().onChildAdded(self)

        self.__window_focused = False
        # self._widget = None
        self._explicitly_hidden = False
        self._shown = True
        # The timer id, set when starting an interval timer. Will be checked
        # by the event filter
        self.__timer_id = None

        # Used by fsui.content.get_parent
        self.internalCachedParent: Optional[Widget]
        # Used by fsui.content.get_window
        self.internalCachedWindow: TopLevelWidget

        # For debugging purposes, can be used to see from where this widget was
        # created.
        # self._init_stack = traceback.format_stack()

        # Imported here to "fix" import cycle
        from fsui.common.layout import Layout

        self.layout: Optional[Layout] = None
        self.contentMargins = ContentMargins(0, 0, 0, 0)

    def addEventListener(
        self, type: Literal["destroy", "resized"], listener: SimpleCallable
    ) -> None:
        if type == "destroy":
            self.addDestroyListener(listener)
        elif type == "resized":
            self.addResizeListener(listener)
        else:
            raise TypeError(type)

    def addDestroyListener(self, listener: SimpleCallable) -> None:
        self.destroyed.connect(listener)
        # return self

    def addResizeListener(self, listener: SimpleCallable) -> None:
        self.resized.connect(listener)
        # return self

    def disable(self) -> None:
        self.setEnabled(False)

    def enable(self) -> None:
        self.setEnabled(True)

    @overrides
    def eventFilter(self, a0: QObject, a1: QEvent) -> bool:
        obj = a0
        event = a1
        event_type = event.type()
        if event_type == QEvent.Type.Resize:
            if obj == self.qwidget:
                self.on_resize()
        elif event_type == QEvent.Type.Show:
            if obj == self.qwidget:
                self.on_show()
        elif event_type == QEvent.Type.Timer:
            timerEvent = cast(QTimerEvent, event)
            if timerEvent.timerId() == self.__timer_id:
                # print("-> on_timer")
                self.on_timer()
                return True
            # else:
            #     print("other timer event")
        elif event_type == QEvent.Type.WindowActivate:
            # print("activated", obj)
            if obj == self.qwidget:
                if not self.__window_focused:
                    # Important to update this before emitting the signal.
                    self.__window_focused = True
                    # self.window_focus_changed.emit()
                    self.onWindowFocusChanged()
                # return True
        elif event_type == QEvent.Type.WindowDeactivate:
            if obj == self.qwidget:
                # print("deactivateEvent", obj)
                if self.__window_focused:
                    # Important to update this before emitting the signal.
                    self.__window_focused = False
                    # self.window_focus_changed.emit()
                    self.onWindowFocusChanged()
                # return True
        return False

    def focus(self) -> None:
        self.qwidget.setFocus()

    def getFont(self) -> Font:
        return Font(qFont=self.qWidget.font())

    def getHeight(self) -> int:
        return self.qwidget.height()

    def getMinSize(self) -> Size:
        return self.ideal_size()

    def getParent(self) -> "Widget":
        """Return the parent widget or raise an exception.

        This method raises an exception if the widget has no parent (e.g. a
        Window). This simplifies type checking. See also hasParent method."""
        if self._parent is None:
            raise NoParentError("Widget has no parent")
        # noinspection PyCallingNonCallable
        return self._parent()

    def getParentOrNone(self) -> "Optional[Widget]":
        try:
            return self.getParent()
        except NoParentError:
            return None

    def getPosition(self) -> Point:
        return self.getRealPosition()

    def getPositionInScreenCoordinates(self) -> Point:
        widget: Optional[Widget] = self
        wx = 0
        wy = 0
        while widget:
            pos = widget.getRealPosition()
            wx += pos[0]
            wy += pos[1]
            widget = widget.getParentOrNone()
        return wx, wy

    def getQWidget(self) -> QWidget:
        if self.__qwidget is None:
            raise RuntimeError("Widget does not have qwidget")
        return self.__qwidget

    def getRealPosition(self) -> Point:
        # return self.qwidget.x(), self.qwidget.y()
        pos = self.qwidget.pos()
        return pos.x(), pos.y()

    def getRealSize(self) -> Size:
        # return self.qwidget.width(), self.qwidget.height()
        size = self.qwidget.size()
        return size.width(), size.height()

    def getSize(self) -> Size:
        return self.getRealSize()

    def getWidth(self) -> int:
        return self.qwidget.width()

    # FIXME: Returning Any on purpose here - now - to avoid circular
    # dependencies. This should be handled better.
    def getWindow(self) -> Any:
        if self._window is None:
            # return None
            raise RuntimeError("No window")
        window = self._window()
        if window is None:
            # return None
            raise RuntimeError("No window")
        return window

    def getX(self) -> int:
        return self.qwidget.x()

    def getY(self) -> int:
        return self.qwidget.y()

    def isWindowFocused(self) -> bool:
        return self.__window_focused

    def hasParent(self) -> bool:
        return self._parent is not None

    def hide(self) -> None:
        self.setVisible(False)

    def isEnabled(self) -> bool:
        return self.qwidget.isEnabled()

    def isExplicitlyHidden(self) -> bool:
        return self._explicitly_hidden

    # FIXME: Move to a Cursor / Mouse class instead?
    # E.g. Cursor.hoversOverWidget(widget)
    # or Cursor.isWithinWidgetBoundary(widget)
    def isUnderMouse(self) -> bool:
        # underMouse does not seem to work "correctly" when the mouse button is
        # kept pressed. The docs say "This value is not updated properly during
        # drag and drop operations."
        # return self.qwidget.underMouse()

        def isMouseWithinWidget(widget: Widget):
            wx, wy = widget.getPositionInScreenCoordinates()
            ww, wh = widget.getSize()
            mx, my = get_mouse_position()
            if mx >= wx and my >= wy and mx < wx + ww and my < wy + wh:
                return True
            else:
                return False

        return isMouseWithinWidget(self)

    def isVisible(self) -> bool:
        return self.qwidget.isVisible()

    def listen(
        self, event: EventHelper[TEvent], listener: EventListener[TEvent]
    ) -> None:
        self.addDestroyListener(event.addListener(listener))

    def runTask(
        self,
        task: Task[T],
        onResult: Callable[[T], None],
        onError: Optional[Callable[[Exception], None]] = None,
        onProgress: Optional[Callable[[str], None]] = None,
    ):
        self.addDestroyListener(
            AsyncSingleTaskRunner(task, onResult, onError, onProgress)
            .start()
            .cancel
        )

    def onChildAdded(self, widget: "Widget") -> None:
        pass

    def onDestroy(self) -> None:
        pass
        # print("Widget.onDestroy", self)

    def onQWidgetChildAdded(self, qwidget: QWidget) -> None:
        pass

    @property
    def qWidget(self) -> QWidget:
        if self.__qwidget is None:
            raise RuntimeError("Widget does not have qwidget")
        return self.__qwidget

    def removeDestroyListener(self, listener: SimpleCallable) -> None:
        self.resized.disconnect(listener)  # type: ignore

    def removeResizeListener(self, listener: SimpleCallable) -> None:
        self.resized.disconnect(listener)  # type: ignore

    def setBackgroundColor(self, color: Color) -> None:
        # FIXME: Check if background_color is already set
        w = self.qwidget
        if color is not None:
            w.setAutoFillBackground(True)
            p = w.palette()
            p.setColor(w.backgroundRole(), color)
            w.setPalette(p)
        else:
            print("FIXME: Clear background color")
            w.setAutoFillBackground(False)

    def setEnabled(self, enabled: bool) -> None:
        self.qwidget.setEnabled(enabled)
        # return self

    def setFont(self, font: Font) -> None:
        self.qwidget.setFont(font.qfont)

    def setMoveCursor(self) -> None:
        # FIXME: self.setCursor(Cursor.MOVE)?
        self.qwidget.setCursor(Qt.CursorShape.SizeAllCursor)

    def setNormalCursor(self) -> None:
        # FIXME: self.setCursor(Cursor.DEFAULT)?
        self.qwidget.setCursor(Qt.CursorShape.ArrowCursor)

    def setPointingHandCursor(self) -> None:
        self.qwidget.setCursor(Qt.CursorShape.PointingHandCursor)

    def setPosition(self, position: Point) -> None:
        self.qwidget.move(position[0], position[1])

    def setPositionAndSize(self, position: Point, size: Size) -> None:
        # FIXME forcing int unsure why coming in as a float
        self.qwidget.setGeometry(position[0], int(position[1]), size[0], size[1])
        # return self

    def setQWidget(self, qwidget: QWidget) -> None:
        self.__qwidget = qwidget
        self.qwidget.installEventFilter(self)
        self.qwidget.destroyed.connect(self.__on_destroyed)  # type: ignore

    def setResizeCursor(self) -> None:
        # FIXME: self.setCursor(Cursor.RESIZE)?
        self.qwidget.setCursor(Qt.CursorShape.SizeFDiagCursor)

    def setSize(self, size: Size) -> None:
        self.qwidget.resize(size[0], size[1])
        # return self

    def setToolTip(self, text: str) -> None:
        self.qwidget.setToolTip(text)

    def setVisible(self, visible: bool = True) -> None:
        # was_shown = self._shown
        if visible:
            self.qwidget.show()
        else:
            self.qwidget.hide()
        self._explicitly_hidden = not visible
        self._shown = visible
        # return was_shown != visible

    # def setWidth(self, width: int):
    #     self.qwidget.resi

    def show(self) -> None:
        self.setVisible(True)

    # -------------------------------------------------------------------------

    # FIXME: Deprecated?
    def widget(self) -> QWidget:
        return self._widget

    @deprecated
    def window_focus(self) -> bool:
        # return self.__window_focused
        return self.isWindowFocused()

    def start_timer(self, interval: int) -> None:
        self.__timer_id = self.qwidget.startTimer(interval)

    # FIXME: When is this used?
    def refresh(self) -> None:
        return self.qwidget.update()

    @deprecated
    def set_background_color(self, color: Color) -> None:
        self.setBackgroundColor(color)

    def set_min_height(self, height: int) -> None:
        # noinspection PyAttributeOutsideInit
        self.min_height = height
        # This is important for splitters (based on QSplitter) to work
        # properly.
        self.qwidget.setMinimumHeight(height)

    def set_min_size(self, size: Size) -> None:
        # noinspection PyAttributeOutsideInit
        self.min_width = size[0]
        # noinspection PyAttributeOutsideInit
        self.min_height = size[1]

        # This is important for splitters (based on QSplitter) to work
        # properly.
        self.qwidget.setMinimumWidth(size[0])
        self.qwidget.setMinimumHeight(size[1])

    def set_min_width(self, width: int) -> None:
        # noinspection PyAttributeOutsideInit
        self.min_width = width
        # This is important for splitters (based on QSplitter) to work
        # properly.
        self.qwidget.setMinimumWidth(width)

    # -------------------------------------------------------------------------

    # FIXME: Move this to PopupMenu instead?
    def popup_menu(
        self, menu: PopupMenu, pos: Point = (0, 0), blocking: bool = True
    ) -> None:
        # popup does not block, and if menu goes out of the scope of the
        # caller, it will disappear (unless we keep a reference here
        # FIXME: using exec now
        # self.__last_popup_menu = menu
        widget = getattr(self, "_widget", self)
        global_pos = widget.mapToGlobal(QPoint(pos[0], pos[1]))
        menu.setParent(self)
        if blocking:
            menu.qmenu.exec(global_pos)
        else:
            menu.qmenu.popup(global_pos)

        # Firing off a fake mouse left up event really assumes that the
        # menu was opened with a left down event, so implementation isn't
        # ideal. Better to add a listener to menu close instead.

        # if hasattr(self, "on_left_up"):
        #     self.on_left_up()

    # -------------------------------------------------------------------------

    def get_background_color(self) -> Color:
        # noinspection PyUnresolvedReferences
        # FIXME: Use cached value from set_background_color?
        return Color(self.qwidget.palette().color(QPalette.ColorRole.Window))

    def get_container(self) -> QWidget:
        return self.widget()

    def ideal_height(self, width: int) -> int:
        return self.ideal_size_for_dimension(1, width=width)

    def ideal_width(self) -> int:
        return self.ideal_size_for_dimension(0)

    def ideal_size(self) -> Size:
        width = self.ideal_width()
        height = self.ideal_height(width)
        return (width, height)

    def ideal_size_for_dimension(
        self, d: Union[Literal[0], Literal[1]], width: Optional[int] = None
    ) -> Size:
        widget = getattr(self, "_widget", self)
        size = 0

        style = getattr(self, "style", {})
        min_size = style.get("minWidth" if d == 0 else "minHeight")
        max_size = style.get("maxWidth" if d == 0 else "maxHeight")
        size = style.get("width" if d == 0 else "height")

        if min_size is None:
            min_size = getattr(
                self, "min_width" if d == 0 else "min_height", None
            )
            # min_width = self.min_width

        def clamp_size(
            size: int, min_size: Optional[int], max_size: Optional[int]
        ) -> int:
            if max_size is not None:
                size = min(size, max_size)
            if min_size is not None:
                size = max(size, min_size)
            return size

        if size is not None:
            if max_size is not None:
                size = min(size, max_size)
            if min_size is not None:
                size = max(size, min_size)
            return clamp_size(size, min_size, max_size)

        # Imported here to "fix" import cycle
        from fsui.common.layout import Layout

        if hasattr(self, "layout") and isinstance(self.layout, Layout):
            if d == 0:
                size = self.layout.get_min_width()
            else:
                assert width is not None
                size = self.layout.get_min_height(width)
            # if hasattr(self, "style"):
            if d == 0:
                size += style.get("paddingLeft", 0) + style.get(
                    "paddingRight", 0
                )
            else:
                size += style.get("paddingTop", 0) + style.get(
                    "paddingBottom", 0
                )
            # size = max(layout_size, size)
            # return size
            return clamp_size(size, min_size, max_size)
        # result = max(width, widget.minimumSizeHint().width())
        # if widget.maximumWidth():
        #     print(widget.maximumWidth())
        #     return min(result, widget.maximumWidth())
        # return min(result, widget.maximumWidth())
        # return result
        if d == 0:
            # result = max(size, widget.minimumSizeHint().width())
            size = widget.minimumSizeHint().width()
        else:
            # result = max(size, widget.minimumSizeHint().height())
            size = widget.minimumSizeHint().height()
        # return min(result, widget.maximumWidth())
        if max_size is not None:
            size = min(size, max_size)
        if min_size is not None:
            size = max(size, min_size)
        return clamp_size(size, min_size, max_size)

    def get_min_height(self, width: int) -> int:
        return self.ideal_size_for_dimension(1, width=width)
        # widget = getattr(self, "_widget", self)
        # assert isinstance(widget, QWidget)
        # height = 0
        # if hasattr(self, "min_height"):
        #     if self.min_height:
        #         height = max(self.min_height, height)
        # if hasattr(self, "layout") and isinstance(self.layout, Layout):
        #     layout_height = self.layout.get_min_height(width)

        #     if hasattr(self, "style"):
        #         print(self, "layout_height", layout_height)
        #         layout_height += self.style.padding_top + self.style.padding_bottom
        #         # if self.style.padding_top or self.style.padding_bottom:
        #         print("+ padding", self.style.padding_top, self.style.padding_bottom)
        #     height = max( layout_height, height)
        #     return height
        # return max(height, widget.minimumSizeHint().height())
        # # return max(height, widget.minimumHeight())

    def get_min_width(self) -> int:
        return self.ideal_size_for_dimension(0)
        # widget = getattr(self, "_widget", self)
        # width = 0

        # style = getattr(self, "style", {})
        # min_width = style.get("minWidth")
        # max_width = style.get("maxWidth")
        # width = style.get("width")

        # if min_width is None and hasattr(self, "min_width"):
        #     min_width = self.min_width

        # if hasattr(self, "min_width"):
        #     if self.min_width:
        #         width = max(self.min_width, width)
        # if hasattr(self, "width"):
        #     pass
        # if hasattr(self, "layout") and isinstance(self.layout, Layout):
        #     layout_width = self.layout.get_min_width()
        #     if hasattr(self, "style"):
        #         layout_width += self.style.padding_left + self.style.padding_right
        #     width = max(layout_width, width)
        #     return width
        # # result = max(width, widget.minimumSizeHint().width())
        # # if widget.maximumWidth():
        # #     print(widget.maximumWidth())
        # #     return min(result, widget.maximumWidth())
        # # return min(result, widget.maximumWidth())
        # # return result
        # result = max(width, widget.minimumSizeHint().width())
        # return min(result, widget.maximumWidth())
        # # return max(width, widget.minimumWidth())

    def __on_destroyed(self) -> None:
        # print(f"Widget.__on_destroyed self={self}")
        self.destroyed.emit()
        self.onDestroy()

    def on_resize(self) -> None:
        # Imported here to "fix" import cycle
        from fsui.common.layout import Layout

        if hasattr(self, "layout") and isinstance(self.layout, Layout):

            width, height = self.getSize()

            # This is mostly used by windows with client-size decorations
            x = self.contentMargins.left
            y = self.contentMargins.top
            width = (
                width - self.contentMargins.left - self.contentMargins.right
            )
            height = (
                height - self.contentMargins.top - self.contentMargins.bottom
            )

            if hasattr(self, "style"):
                style = cast(Style, getattr(self, "style"))
                x += style.padding_left
                y += style.padding_top
                width -= x + style.padding_right
                height -= y + style.padding_bottom

            self.layout.set_position((x, y))
            self.layout.set_size((width, height))
            self.layout.update()
        self.resized.emit()

    def on_show(self):
        self.on_resize()
        self.shown.emit()

    def on_timer(self):
        pass

    def onWindowFocusChanged(self):
        # FIXME: Do not let all widgets subscribe to this event automatically?
        pass

    # -------------------------------------------------------------------------
    # Deprecated
    # -------------------------------------------------------------------------

    @deprecated
    def set_tooltip(self, tooltip: str):
        self.setToolTip(tooltip)

    @deprecated
    def measure_text(self, text: str):
        return self.getFont().measureText(text)

    @deprecated
    def set_hand_cursor(self) -> None:
        self.setPointingHandCursor()

    @deprecated
    def set_move_cursor(self) -> None:
        self.setMoveCursor()

    @deprecated
    def set_resize_cursor(self) -> None:
        self.setResizeCursor()

    @deprecated
    def set_normal_cursor(self) -> None:
        self.setNormalCursor()

    @deprecated
    def set_enabled(self, enabled: bool = True) -> None:
        self.setEnabled(enabled)

    @deprecated
    def set_font(self, font: Font) -> None:
        self.setFont(font)

    @deprecated
    def enabled(self) -> bool:
        return self.isEnabled()

    @deprecated
    def explicitly_hidden(self) -> bool:
        return self.isExplicitlyHidden()

    @deprecated
    def font(self) -> Font:
        return self.getFont()

    @deprecated
    def get_font(self) -> Font:
        return self.getFont()

    @deprecated
    def get_parent(self) -> "Widget":
        return self.getParent()

    @deprecated
    def get_position(self) -> Point:
        return self.getPosition()

    @deprecated
    def get_size(self) -> Size:
        return self.getSize()

    @deprecated
    def get_window(self):
        return self.getWindow()

    @deprecated
    def height(self) -> int:
        return self.getHeight()

    @deprecated
    def is_enabled(self) -> bool:
        return self.isEnabled()

    @deprecated
    def is_visible(self) -> bool:
        return self.isVisible()

    @deprecated
    def is_under_mouse(self) -> bool:
        return self.isUnderMouse()

    @deprecated
    def parent(self) -> "Optional[Widget]":
        return self.getParentOrNone()

    @deprecated
    def position(self) -> Point:
        return self.getPosition()

    @deprecated
    def set_position(
        self, position: Union[Point, int], y: Optional[int] = None
    ) -> None:
        if y is None:
            self.qwidget.move(position[0], position[1])  # type: ignore
        else:
            self.qwidget.move(position, y)  # type: ignore

    @deprecated
    def set_position_and_size(self, position: Point, size: Size) -> None:
        self.setPositionAndSize(position, size)

    @deprecated
    def set_size(self, size: Size) -> None:
        self.setSize(size)

    @deprecated
    def set_visible(self, show: bool = True) -> None:
        self.setVisible(show)

    # @deprecated
    # def set_widget(self, widget: QWidget) -> None:
    #     self.setQWidget(widget)

    @deprecated
    def show_or_hide(self, show: bool = True) -> None:
        self.setVisible(show)

    @deprecated
    def size(self) -> Size:
        return self.getSize()

    @deprecated
    def visible(self) -> bool:
        return self.isVisible()

    # FIXME: Deprecated
    @property
    def _widget(self) -> QWidget:
        return self.qwidget

    @deprecated
    def width(self) -> int:
        return self.getWidth()

    @property  # type: ignore
    @deprecated
    def window(self):
        return self.getWindow()

    @property  # type: ignore
    @deprecated
    def _qwidget(self) -> Optional[QWidget]:
        # return self.__qwidget()
        return self.__qwidget

    @property
    def qwidget(self) -> QWidget:
        return self.qWidget
