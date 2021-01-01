import datetime
import math

from fsui import Label, Font
from fsui.qt import Qt, QRect, QWidget, QPainter, QBrush, QPen, QColor
from fsui.qt.qparent import QParent
from fsui.qt.widget import Widget
from launcher.system.classes.window import Window
from launcher.system.classes.windowresizehandle import WindowResizeHandle


# TODO: Add support for alarm, digital display, date display on/off (etc) like
# the original


class ClockWindow(Window):
    def __init__(self, parent):
        super().__init__(parent, title="Clock", maximizable=False)
        self.clock = ClockWidget(self)
        self.layout.add(
            self.clock, fill=True, expand=True, margin=20, margin_bottom=10
        )
        self.clock.set_min_size((200, 200))
        self.label = Label(self, "0000-00-00")
        self.label.set_text_alignment(Label.TEXT_ALIGNMENT_CENTER)
        self.label.set_font(
            Font.from_description("Saira Condensed Semi-Bold 20")
        )
        self.layout.add(self.label, fill=True, margin=10, margin_top=0)

        self.old_time = None
        self.update_clock()
        self.start_timer(100)

        WindowResizeHandle(self)

    def on_timer(self):
        self.update_clock()

    def update_clock(self):
        now = datetime.datetime.now()
        new_time = (
            now.year,
            now.month,
            now.day,
            now.hour,
            now.minute,
            now.second,
        )
        if new_time != self.old_time:
            self.old_time = new_time
            self.label.set_text("{0}-{1:02d}-{2:02d}".format(*new_time))
            self.clock.set_time(new_time)


class ClockWidget(Widget):
    def __init__(self, parent):
        super().__init__(parent, ClockQWidget(QParent(parent)))

    def set_time(self, new_time):
        self._widget.time = new_time
        self.refresh()


class ClockQWidget(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("Clock")
        self.time = (0, 0, 0, 0, 0, 0)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing)
        pen = QPen(QColor(0x80, 0x80, 0x80))
        pen.setWidth(2)
        painter.setPen(pen)
        painter.setBrush(QBrush(Qt.white))
        x = 1
        y = 1
        w = self.width() - 2
        h = self.height() - 2

        rect = QRect(x, y, w, h)
        painter.drawEllipse(rect)

        cx = x + w / 2
        cy = y + h / 2
        a = w / 2 * 0.85
        b = h / 2 * 0.85

        pen.setWidth(0)
        painter.setPen(pen)
        painter.setBrush(QBrush(Qt.black))

        for i in range(12):
            px = cx + a * math.cos(2 * math.pi * i / 12)
            py = cy + b * math.sin(2 * math.pi * i / 12)
            painter.drawEllipse(px - 3, py - 3, 6, 6)

        hours, minutes, seconds = self.time[3:]
        minutes += seconds / 60.0
        hours += minutes / 60.0

        a = w / 2 * 0.6
        b = h / 2 * 0.6
        pen.setWidth(4)
        painter.setPen(pen)
        self.draw_hand_line(
            painter, w, h, cx, cy, a, b, 2.0 * math.pi * hours / 12
        )

        a = w / 2 * 0.8
        b = h / 2 * 0.8
        pen.setWidth(3)
        painter.setPen(pen)
        self.draw_hand_line(
            painter, w, h, cx, cy, a, b, 2.0 * math.pi * minutes / 60
        )

        pen = QPen(QColor(0xFF, 0x00, 0x00))
        pen.setWidth(2)
        painter.setPen(pen)
        self.draw_hand_line(
            painter, w, h, cx, cy, a, b, 2.0 * math.pi * seconds / 60
        )

    def draw_hand_line(self, painter, w, h, cx, cy, a, b, degrees):
        f2 = -math.pi / 2.0
        painter.drawLine(
            cx,
            cy,
            cx + a * math.cos(degrees + f2),
            cy + b * math.sin(degrees + f2),
        )
