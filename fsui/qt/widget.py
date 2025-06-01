from typing import Tuple
import warnings

from fsui.common.layout import Layout
from fsui.qt import QPoint
from fsui.qt import Qt, QObject, QFontMetrics, QWidget, QPalette, QCursor
from fsui.qt.Color import Color
from fsui.qt.DrawingContext import Font
from fsui.qt.signal import Signal


# noinspection PyPep8Naming
class Widget(QObject):

    destroyed = Signal()

    def __init__(self, parent, *_):
        super().__init__()
        self._parent = None
        # noinspection PyProtectedMember
        self._window = parent._window
        self._widget = None
        self._explicitly_hidden = False

    def widget(self):
        return self._widget

    def get_container(self):
        return self.widget()

    def set_widget(self, widget):
        self._widget = widget
        # self.init_mixin_base()
        # self.layout = None
        # self._parent = weakref.ref(parent)
        # noinspection PyProtectedMember
        # self._window = parent._window
        # widget = getattr(self, "_widget", self)
        # widget.move(10000, 10000)

        # if self.get_window() != widget:
        # assert isinstance(widget, QWidget)

        widget.installEventFilter(self)
        widget.destroyed.connect(self.on_destroy)

    def on_destroy(self):
        print("Widget.on_destroy", self)
        self.destroyed.emit()

    def explicitly_hidden(self):
        return self._explicitly_hidden

    def set_visible(self, show=True):
        if show:
            self.widget().show()
        else:
            self.widget().hide()
        self._explicitly_hidden = not show

    def show(self):
        self.set_visible(True)

    def hide(self):
        self.set_visible(False)

    def eventFilter(self, obj, event):
        return False

    def parent(self):
        if self._parent is None:
            return None
        # noinspection PyCallingNonCallable
        return self._parent()

    def font(self):
        return Font(self.widget().font())

    def set_font(self, font):
        self.widget().setFont(font.font)

    def is_visible(self):
        return self.widget().isVisible()

    def measure_text(self, text):
        font = self.widget().font()
        metrics = QFontMetrics(font)
        rect = metrics.boundingRect(text)
        return rect.width(), rect.height()

    def set_hand_cursor(self):
        self.widget().setCursor(Qt.PointingHandCursor)

    def set_normal_cursor(self):
        self.widget().setCursor(Qt.ArrowCursor)

    def is_enabled(self):
        return self.widget().isEnabled()

    def focus(self):
        self.widget().setFocus()

    def refresh(self):
        return self.widget().update()

    def set_min_size(self, size):
        # noinspection PyAttributeOutsideInit
        self.min_width = size[0]
        # noinspection PyAttributeOutsideInit
        self.min_height = size[1]

    def set_min_width(self, width):
        # noinspection PyAttributeOutsideInit
        self.min_width = width

    def set_min_height(self, height):
        # noinspection PyAttributeOutsideInit
        self.min_height = height

    def get_min_width(self):
        widget = getattr(self, "_widget", self)
        width = 0
        if hasattr(self, "min_width"):
            if self.min_width:
                width = max(self.min_width, width)
        if hasattr(self, "layout") and isinstance(self.layout, Layout):
            width = max(self.layout.get_min_width(), width)
            return width
        # result = max(width, widget.minimumSizeHint().width())
        # if widget.maximumWidth():
        #     print(widget.maximumWidth())
        #     return min(result, widget.maximumWidth())
        # return min(result, widget.maximumWidth())
        # return result
        result = max(width, widget.minimumSizeHint().width())
        return min(result, widget.maximumWidth())
        # return max(width, widget.minimumWidth())

    def get_min_height(self):
        widget = getattr(self, "_widget", self)
        assert isinstance(widget, QWidget)
        height = 0
        if hasattr(self, "min_height"):
            if self.min_height:
                height = max(self.min_height, height)
        if hasattr(self, "layout") and isinstance(self.layout, Layout):
            height = max(self.layout.get_min_height(), height)
            return height
        return max(height, widget.minimumSizeHint().height())
        # return max(height, widget.minimumHeight())

    def set_position(self, position, y=None):
        if y is None:
            self.widget().move(*position)
        else:
            self.widget().move(position, y)

    def set_size(self, size):
        self.widget().resize(*size)

    def set_position_and_size(self, position, size):
        self.widget().setGeometry(position[0], position[1], size[0], size[1])

    @property
    def window(self):
        # noinspection PyCallingNonCallable
        return self._window()

    def get_window(self):
        warnings.warn("use window property instead", DeprecationWarning)
        # noinspection PyCallingNonCallable
        return self._window()

    def position(self):
        return self.widget().x(), self.widget().y()

    def size(self):
        return self.widget().width(), self.widget().height()

    def width(self):
        return self.size()[0]

    def height(self):
        return self.size()[1]

    def set_tool_tip(self, tool_tip):
        widget = getattr(self, "_widget", self)
        widget.setToolTip(tool_tip)

    def set_tooltip(self, tool_tip):
        self.set_tool_tip(tool_tip)

    def disable(self):
        return self.enable(False)

    def enable(self, enable=True):
        widget = getattr(self, "_widget", self)
        widget.setEnabled(enable)

    def set_enabled(self, enable=True):
        self.enable(enable)

    def on_resize(self):
        if hasattr(self, "layout") and isinstance(self.layout, Layout):
            self.layout.set_size(self.get_size())
            self.layout.update()

    def get_background_color(self):
        # noinspection PyUnresolvedReferences
        return Color(self.widget().palette().color(QPalette.ColorRole.Window))

    def set_background_color(self, color):
        widget = self.widget()
        widget.setAutoFillBackground(True)
        p = widget.palette()
        p.setColor(widget.backgroundRole(), color)
        widget.setPalette(p)

    def popup_menu(self, menu, pos=(0, 0), blocking=True):
        # popup does not block, and if menu goes out of the scope of the
        # caller, it will disappear (unless we keep a reference here
        # FIXME: using exec now
        # self.__last_popup_menu = menu
        widget = getattr(self, "_widget", self)
        global_pos = widget.mapToGlobal(QPoint(pos[0], pos[1]))
        menu.set_parent(self)
        if blocking:
            menu.qmenu.exec(global_pos)
        else:
            menu.qmenu.popup(global_pos)

        # Firing off a fake mouse left up event really assumes that the
        # menu was opened with a left down event, so implementation isn't
        # ideal. Better to add a listener to menu close instead.

        # if hasattr(self, "on_left_up"):
        #     self.on_left_up()

    def is_mouse_over(self):
        # # noinspection PyArgumentList
        # c = QCursor.pos()
        # # noinspection PyUnresolvedReferences
        # p = self.widget().mapToGlobal(QPoint(0, 0))
        # s = self.size()
        # print(c, p, s)
        # if p.x() <= c.x() < p.x() + s[0] and p.y() <= c.y() < p.y() + s[1]:
        #     return True
        # return False
        return self.widget().underMouse()

    # DEPRECATED
    def get_parent(self):
        return self.parent()

    # DEPRECATED
    def visible(self):
        return self.is_visible()

    # DEPRECATED
    def get_font(self):
        return self.font()

    # DEPRECATED
    def show_or_hide(self, show=True):
        self.set_visible(show)

    # DEPRECATED
    def get_position(self):
        return self.position()

    # DEPRECATED
    def get_size(self) -> Tuple[int, int]:
        return self.size()
