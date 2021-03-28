import traceback
from weakref import ref

from fspy.decorators import deprecated
from fsui.common.layout import Layout
from fsui.qt import (
    QEvent,
    QFontMetrics,
    QObject,
    QPalette,
    QPoint,
    Qt,
    QWidget,
)
from fsui.qt.color import Color
from fsui.qt.font import Font
from fsui.qt.mouse import get_mouse_position
from fsui.qt.signal import Signal

# import fsui.qt.window

# noinspection PyPep8Naming
class Widget(QObject):
    # FIXME: Consider renaming to destroy, since the signal is sent before
    # the object is deleted and children are destroyed
    destroyed = Signal()
    # FIXME: Only toplevel need to have a signal and sent out notifications
    # window_focus_changed = Signal()
    shown = Signal()

    resized = Signal()

    def __init__(self, parent, qwidget):
        super().__init__()
        # self._widget = widget
        # self.__qwidget = ref(widget)  # ??
        self.__qwidget = None
        if qwidget is not None:
            self.set_qwidget(qwidget)

        if parent is not None:
            self._parent = ref(parent)
            # noinspection PyProtectedMember
            self._window = parent._window
        else:
            self._parent = None

        self.__window_focus = False
        # self._widget = None
        self._explicitly_hidden = False
        self._shown = True
        # The timer id, set when starting an interval timer. Will be checked
        # by the event filter
        self.__timer_id = None

        # For debugging purposes, can be used to see from where this widget was
        # created.
        # self._init_stack = traceback.format_stack()

    @deprecated
    def disable(self):
        return self.set_enabled(False)

    @deprecated
    def enable(self, enable=True):
        self.set_enabled(enable)

    def enabled(self):
        return self._qwidget.isEnabled()

    def eventFilter(self, obj, event):
        event_type = event.type()
        if event_type == QEvent.Resize:
            if obj == self._qwidget:
                self.on_resize()

        elif event_type == QEvent.Show:
            if obj == self._qwidget:
                self.on_show()

        elif event_type == QEvent.Timer:
            if event.timerId() == self.__timer_id:
                # print("-> on_timer")
                self.on_timer()
                return True
            # else:
            #     print("other timer event")

        elif event_type == QEvent.WindowActivate:
            # print("activated", obj)
            if obj == self._qwidget:
                if not self.__window_focus:
                    # Important to update this before emitting the signal.
                    self.__window_focus = True
                    # self.window_focus_changed.emit()
                    self.on_window_focus_changed()
                # return True
        elif event_type == QEvent.WindowDeactivate:
            if obj == self._qwidget:
                # print("deactivateEvent", obj)
                if self.__window_focus:
                    # Important to update this before emitting the signal.
                    self.__window_focus = False
                    # self.window_focus_changed.emit()
                    self.on_window_focus_changed()
                # return True

        return False

    def explicitly_hidden(self):
        return self._explicitly_hidden

    def focus(self):
        self._qwidget.setFocus()

    def font(self):
        return Font(self._qwidget.font())

    def get_background_color(self):
        # noinspection PyUnresolvedReferences
        # FIXME: Use cached value from set_background_color?
        return Color(self._qwidget.palette().color(QPalette.Window))

    def get_container(self):
        return self.widget()

    @deprecated
    def get_font(self):
        return self.font()

    def ideal_height(self, width):
        return self.ideal_size_for_dimension(1, width=width)

    def ideal_width(self):
        return self.ideal_size_for_dimension(0)

    def ideal_size(self):
        width = self.ideal_width()
        height = self.ideal_height(width)
        return (width, height)

    def ideal_size_for_dimension(self, d, width=None):
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

        def clamp_size(size, min_size, max_size):
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

        if hasattr(self, "layout") and isinstance(self.layout, Layout):
            if d == 0:
                size = self.layout.get_min_width()
            else:
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

    def get_min_height(self, width):
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

    def get_min_width(self):
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

    @deprecated
    def get_parent(self):
        return self.parent()

    @deprecated
    def get_position(self):
        return self.position()

    @deprecated
    def get_size(self):
        return self.size()

    @deprecated
    def get_window(self):
        # noinspection PyCallingNonCallable
        return self._window()

    def height(self):
        return self.size()[1]

    def hide(self):
        self.set_visible(False)

    def is_enabled(self):
        return self._qwidget.isEnabled()

    @deprecated
    def is_visible(self):
        return self.visible()

    def is_under_mouse(self):
        # underMouse does not seem to work "correctly" when the mouse button is
        # kept pressed. The docs say "This value is not updated properly during
        # drag and drop operations."
        # return self._qwidget.underMouse()

        def get_absolute_widget_position(widget):
            wx = 0
            wy = 0
            while widget:
                pos = widget.position()
                wx += pos[0]
                wy += pos[1]
                widget = widget.parent()
            return wx, wy

        def is_mouse_within_widget(widget):
            wx, wy = get_absolute_widget_position(widget)
            ww, wh = widget.size()
            mx, my = get_mouse_position()
            if mx >= wx and my >= wy and mx < wx + ww and my < wy + wh:
                return True
            else:
                return False

        return is_mouse_within_widget(self)

    def measure_text(self, text):
        font = self._qwidget.font()
        metrics = QFontMetrics(font)
        return metrics.width(text), metrics.height()

    def on_destroy(self):
        self.destroyed.emit()

    def __on_destroyed(self):
        # print(f"Widget.__on_destroyed self={self}")
        self.on_destroy()

    def on_resize(self):
        if hasattr(self, "layout") and isinstance(self.layout, Layout):
            if hasattr(self, "style"):
                x = self.style.padding_left
                y = self.style.padding_top
                width, height = self.size()
                width -= x + self.style.padding_right
                height -= y + self.style.padding_bottom
                self.layout.set_position((x, y))
                self.layout.set_size((width, height))
            else:
                self.layout.set_size(self.size())
            self.layout.update()
        self.resized.emit()

    def on_show(self):
        self.on_resize()
        self.shown.emit()

    def on_timer(self):
        pass

    def on_window_focus_changed(self):
        pass

    def parent(self):
        return self.getParent()

    def getParent(self):
        if self._parent is None:
            return None
        # noinspection PyCallingNonCallable
        return self._parent()

    def popup_menu(self, menu, pos=(0, 0), blocking=True):
        # popup does not block, and if menu goes out of the scope of the
        # caller, it will disappear (unless we keep a reference here
        # FIXME: using exec now
        # self.__last_popup_menu = menu
        widget = getattr(self, "_widget", self)
        global_pos = widget.mapToGlobal(QPoint(pos[0], pos[1]))
        menu.set_parent(self)
        if blocking:
            menu.qmenu.exec_(global_pos)
        else:
            menu.qmenu.popup(global_pos)

        # Firing off a fake mouse left up event really assumes that the
        # menu was opened with a left down event, so implementation isn't
        # ideal. Better to add a listener to menu close instead.

        # if hasattr(self, "on_left_up"):
        #     self.on_left_up()

    def position(self):
        pos = self._qwidget.pos()
        return pos.x(), pos.y()

    @property
    def _qwidget(self):
        # return self.__qwidget()
        return self.__qwidget

    def refresh(self):
        return self._qwidget.update()

    def set_background_color(self, color):
        # FIXME: Check if background_color is already set
        w = self._qwidget
        if color is not None:
            w.setAutoFillBackground(True)
            p = w.palette()
            p.setColor(w.backgroundRole(), color)
            w.setPalette(p)
        else:
            print("FIXME: Clear background color")
            w.setAutoFillBackground(False)

    def set_enabled(self, enabled=True):
        self._qwidget.setEnabled(enabled)

    def set_font(self, font):
        self._qwidget.setFont(font.font)

    def set_hand_cursor(self):
        self._qwidget.setCursor(Qt.PointingHandCursor)

    def set_min_height(self, height):
        # noinspection PyAttributeOutsideInit
        self.min_height = height

    def set_min_size(self, size):
        # noinspection PyAttributeOutsideInit
        self.min_width = size[0]
        # noinspection PyAttributeOutsideInit
        self.min_height = size[1]

    def set_min_width(self, width):
        # noinspection PyAttributeOutsideInit
        self.min_width = width

    def set_move_cursor(self):
        self._qwidget.setCursor(Qt.SizeAllCursor)

    def set_resize_cursor(self):
        self._qwidget.setCursor(Qt.SizeFDiagCursor)

    def set_normal_cursor(self):
        self._qwidget.setCursor(Qt.ArrowCursor)

    def set_position(self, position, y=None):
        if y is None:
            self._qwidget.move(position[0], position[1])
        else:
            self._qwidget.move(position, y)

    def set_position_and_size(self, position, size):
        self._qwidget.setGeometry(position[0], position[1], size[0], size[1])

    def set_size(self, size):
        self._qwidget.resize(size[0], size[1])

    def set_tooltip(self, tooltip):
        widget = getattr(self, "_widget", self)
        widget.setToolTip(tooltip)

    def set_visible(self, show=True):
        was_shown = self._shown
        if show:
            self._qwidget.show()
        else:
            self._qwidget.hide()
        self._explicitly_hidden = not show
        self._shown = show
        return was_shown != show

    @deprecated
    def set_widget(self, widget):
        self.set_qwidget(widget)

    def set_qwidget(self, widget):
        # self._widget = widget
        # self.__qwidget = ref(widget)
        self.__qwidget = widget
        self._qwidget.installEventFilter(self)
        self._qwidget.destroyed.connect(self.__on_destroyed)

    def show(self):
        self.set_visible(True)

    @deprecated
    def show_or_hide(self, show=True):
        self.set_visible(show)

    def size(self):
        return self._qwidget.width(), self._qwidget.height()

    def start_timer(self, interval):
        self.__timer_id = self._qwidget.startTimer(interval)

    def visible(self):
        return self._qwidget.isVisible()

    # FIXME: Deprecated
    @property
    def _widget(self):
        return self._qwidget

    # FIXME: Deprecated?
    def widget(self):
        return self._widget

    def width(self):
        return self.size()[0]

    @property
    def window(self):
        # noinspection PyCallingNonCallable
        return self._window()

    def getWindow(self):
        return self._window()

    def window_focus(self):
        return self.__window_focus


# from fsui.qt.window import Window
