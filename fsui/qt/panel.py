import traceback
import weakref
from typing import Optional

from fsbc.util import unused
from fsui.common.layout import Layout, VerticalLayout
from fsui.qt.color import Color
from fsui.qt.core import QEvent
from fsui.qt.drawingcontext import DrawingContext
from fsui.qt.gui import (
    QKeyEvent,
    QMouseEvent,
    QPaintEvent,
    QResizeEvent,
    QShowEvent,
)
from fsui.qt.qparent import QParent
from fsui.qt.qt import QPainter, Qt, QWidget
from fswidgets.style import Style
from fswidgets.widget import Widget


class Panel(Widget):
    def __init__(
        self,
        parent: Widget,
        paintable: bool = False,
        style: Optional[Style] = None,
        forceRealParent: bool = False,
    ):
        unused(paintable)
        super().__init__(
            parent,
            WidgetWithEventHandlers(
                QParent(parent, forceRealParent=forceRealParent), self
            ),
        )
        # self.style = style or Style()
        style = style or Style()
        backgroundColor = style.getBackgroundColor()
        if backgroundColor is not None:
            self.set_background_color(Color.fromHex(backgroundColor))
        # Temporarily, delete self.style until API is done, otherwise,
        # FlexLayout will try to look up non-existant properties
        # del self.style

        self._widget.move(0, 2000)

        self._parent = weakref.ref(parent)
        # QWidget.__init__(self, QParent(parent))
        # self.init_widget(parent)
        self.layout: Layout = VerticalLayout()
        # self.layout = None
        self._painter: Optional[QPainter] = None

        # QWidget.__init__(self)
        # self.setParent(parent.get_container())
        # super(Panel, self).__init__(parent.get_container())
        # super().__init__()
        self.internalIgnoreNextLeftDownEvent = False
        # self._widget.setFocusPolicy(Qt.NoFocus)

    # def start_timer(self, interval):
    #     # FIXME: Can maybe to this via Widget and eventFilter instead!
    #     # (Would work for all Widget-wrapped widgets instead)
    #     self._widget.startTimer(interval)

    def on_left_down(self) -> None:
        pass

    def on_left_up(self) -> None:
        pass

    def on_left_dclick(self) -> None:
        pass

    def on_mouse_motion(self) -> None:
        pass

    def on_paint(self) -> None:
        pass

    def create_dc(self) -> DrawingContext:
        if self._painter is None:
            raise RuntimeError(
                "Cannot create DrawingContext at this point (no painter)"
            )
        return DrawingContext(self._painter)

    def on_mouse_enter(self) -> None:
        pass

    def on_mouse_leave(self) -> None:
        pass

    def on_key_press(self, event: QKeyEvent) -> None:
        pass

    # FIXME: add? what is this used for?
    def add(self, child: Layout) -> None:
        if hasattr(self, "set_layout"):
            self.set_layout(child)
        else:
            self.layout = child

    def internalSetPainter(self, painter: Optional[QPainter]) -> None:
        self._painter = painter


# noinspection PyProtectedMember
class WidgetWithEventHandlers(QWidget):
    def __init__(self, parent: QWidget, owner: Panel) -> None:
        # print(f"WidgetWithEventHandlers got parent {parent}")
        super().__init__(parent)
        self._owner = owner

    def enterEvent(self, a0: QEvent) -> None:
        self.owner().on_mouse_enter()

    def keyPressEvent(self, a0: QKeyEvent) -> None:
        self.owner().on_key_press(a0)

    def leaveEvent(self, a0: QEvent) -> None:
        self.owner().on_mouse_leave()

    def mouseDoubleClickEvent(self, a0: QMouseEvent) -> None:
        if a0.button() == Qt.MouseButton.LeftButton:
            self.owner().on_left_dclick()

    def mouseMoveEvent(self, a0: QMouseEvent) -> None:
        self.owner().on_mouse_motion()

    def mousePressEvent(self, a0: QMouseEvent) -> None:
        if a0.button() == Qt.MouseButton.LeftButton:
            # A temp code is made in case internalIgnoreNextLeftDownEvent is
            # altered inside on_left_down.
            ignore = self.owner().internalIgnoreNextLeftDownEvent
            self.owner().internalIgnoreNextLeftDownEvent = False
            if ignore:
                print("internalIgnoreNextLeftDownEvent was True", self)
            else:
                self.owner().on_left_down()

    def mouseReleaseEvent(self, a0: QMouseEvent) -> None:
        if a0.button() == Qt.MouseButton.LeftButton:
            self.owner().on_left_up()

    def owner(self) -> Panel:
        return self._owner

    def paintEvent(self, a0: QPaintEvent) -> None:
        # if not self._paintable:
        #     #dc = wx.PaintDC(self)
        #     return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.owner().internalSetPainter(painter)
        try:
            self.owner().on_paint()
        except Exception:
            traceback.print_exc()
        finally:
            self.owner().internalSetPainter(None)

    def resizeEvent(self, a0: QResizeEvent) -> None:
        self.owner().on_resize()

    def showEvent(self, a0: QShowEvent) -> None:
        self.owner().on_resize()

    # Handled via Widget
    # def timerEvent(self, event):
    #     self.owner().on_timer()
