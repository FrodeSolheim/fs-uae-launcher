import weakref
import traceback
from fsbc.util import unused
from fsui.qt import Qt, QWidget, QPainter
from fsui.qt.helpers import QParent
from fsui.qt.widget import Widget


class Panel(Widget):
    def __init__(self, parent, paintable=False):
        unused(paintable)
        super().__init__(parent)
        self.set_widget(WidgetWithEventHandlers(QParent(parent), self))
        self._widget.move(0, 2000)
        self._widget.setAutoFillBackground(True)

        self._parent = weakref.ref(parent)
        # QWidget.__init__(self, QParent(parent))
        # self.init_widget(parent)
        self.layout = None
        self._painter = None

        # QWidget.__init__(self)
        # self.setParent(parent.get_container())
        # super(Panel, self).__init__(parent.get_container())
        # super().__init__()
        self._ignore_next_left_down_event = False
        # self._widget.setFocusPolicy(Qt.FocusPolicy.NoFocus)

    def on_left_down(self):
        pass

    def on_left_up(self):
        pass

    def on_left_dclick(self):
        pass

    def on_mouse_motion(self):
        pass

    def on_paint(self):
        pass

    def create_dc(self):
        from .DrawingContext import DrawingContext

        return DrawingContext(self._painter)

    def on_mouse_enter(self):
        pass

    def on_mouse_leave(self):
        pass

    def on_key_press(self, event):
        pass

    def add(self, child):
        if hasattr(self, "set_layout"):
            self.set_layout(child)
        else:
            self.layout = child


# noinspection PyProtectedMember
class WidgetWithEventHandlers(QWidget):
    def __init__(self, parent, owner):
        super().__init__(parent)
        self._owner = owner
        # self._painter = None

    def owner(self):
        return self._owner

    def paintEvent(self, event):
        # if not self._paintable:
        #     #dc = wx.PaintDC(self)
        #     return

        self.owner()._painter = QPainter(self)
        self.owner()._painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        # self._painter.setRenderHint(QPainter.Qt4CompatiblePainting)
        try:
            self.owner().on_paint()
        except Exception:
            traceback.print_exc()
        finally:
            self.owner()._painter = None

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            # A temp code is made in case _ignore_next_left_down_event is
            # altered inside on_left_down.
            ignore = self.owner()._ignore_next_left_down_event
            self.owner()._ignore_next_left_down_event = False
            if ignore:
                print("_ignore_next_left_down_event was True", self)
            else:
                self.owner().on_left_down()

    def keyPressEvent(self, event):
        self.owner().on_key_press(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.owner().on_left_up()

    def mouseMoveEvent(self, event):
        self.owner().on_mouse_motion()

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.owner().on_left_dclick()

    def showEvent(self, event):
        self.owner().on_resize()

    def resizeEvent(self, event):
        self.owner().on_resize()

    def enterEvent(self, _):
        self.owner().on_mouse_enter()

    def leaveEvent(self, _):
        self.owner().on_mouse_leave()
