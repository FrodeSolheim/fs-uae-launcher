import math
import datetime
from fsui.qt import Qt, QRect, QLabel, QVBoxLayout, QWidget
from fsui.qt import QPainter, QBrush, QPen, QColor
from fs_uae_workspace.shell import QWindow, SimpleApplication


class ClockWindow(QWindow):

    def __init__(self):
        QWindow.__init__(self, None)
        self.setWindowTitle("Clock")
        layout = QVBoxLayout()
        self.label = QLabel("00:00")
        self.widget = ClockWidget()
        # self.label.show()
        # self.label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        layout.addWidget(self.widget)
        self.setLayout(layout)

        self.resize(200, 200)

    def __del__(self):
        print("ClockWindow.__del__")


class ClockWidget(QWidget):

    def __init__(self):
        QWidget.__init__(self, None)
        self.setWindowTitle("Clock")

        self.time = None
        self.updateClock()
        self.startTimer(100)

    # noinspection PyPep8Naming
    def updateClock(self):
        now = datetime.datetime.now()
        new_time = (now.hour, now.minute, now.second)
        if new_time != self.time:
            self.time = new_time
            self.repaint()

    def timerEvent(self, event):
        self.updateClock()
        import gc
        print(gc.garbage)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing)
        pen = QPen(QColor(0x80, 0x80, 0x80))
        pen.setWidth(2)
        painter.setPen(pen)
        painter.setBrush(QBrush(Qt.white))
        x, y, w, h = 10, 10, self.width() - 20, self.height() - 20
        rect = QRect(x, y, w, h)
        # painter.drawChord(rect, 0, 16 * 360)
        painter.drawEllipse(rect)

        cx = x + w / 2
        cy = y + h / 2
        r = w / 2 - 10

        pen.setWidth(4)
        painter.setPen(pen)

        for i in range(12):
            px = cx + r * math.cos(2 * math.pi * i / 12)
            py = cy + r * math.sin(2 * math.pi * i / 12)
            painter.drawPoint(px, py)

        hours, minutes, seconds = self.time
        minutes += seconds / 60.0
        hours += minutes / 60.0

        f = 2.0 * math.pi
        f2 = - math.pi / 2.0

        r = w / 2 * 0.6
        # pen = QPen(QColor(0xff, 0x00, 0x00))
        pen.setWidth(2)
        painter.setPen(pen)
        painter.drawLine(cx, cy,
                         cx + r * math.cos(f * hours / 12 + f2),
                         cy + r * math.sin(f * hours / 12 + f2))

        r = w / 2 * 0.8
        # pen = QPen(QColor(0xff, 0x00, 0x00))
        pen.setWidth(2)
        painter.setPen(pen)
        painter.drawLine(cx, cy,
                         cx + r * math.cos(f * minutes / 60 + f2),
                         cy + r * math.sin(f * minutes / 60 + f2))

        pen = QPen(QColor(0xff, 0x00, 0x00))
        # pen.setWidth(2)
        painter.setPen(pen)
        painter.drawLine(cx, cy,
                         cx + r * math.cos(f * seconds / 60 + f2),
                         cy + r * math.sin(f * seconds / 60 + f2))

application = SimpleApplication(ClockWindow)
