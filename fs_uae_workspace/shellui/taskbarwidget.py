from fsui.qt import Qt, QWidget, QHBoxLayout, QPushButton, QApplication
from fsui.qt import QPainter, QRect, QPen, QColor, QPoint, QFont


class TaskBarButton(QWidget):

    def __init__(self, parent, window_handler, window):
        super().__init__(parent)
        self.window = window
        self.window_handler = window_handler
        self.window_handler.window_changed.connect(self.__window_changed)

        self.setFixedHeight(parent.height())
        self.setMaximumWidth(300)
        self.setMinimumWidth(200)

        # self.setAutoFillBackground(True)
        self.setStyleSheet("""
            font-family: "Open Sans";
            font-size: 10pt;
            /* font-weight: bold; */
            /* background-color: #282828; */
            background-color: #000000;
        """)

    def disconnect(self):
        self.window_handler.window_changed.disconnect(self.__window_changed)
        self.window_handler = None
        self.window = None

    def __window_changed(self, window):
        if window != self.window:
            return
        if window.changed == "name":
            self.update()
        elif window.changed == "active":
            self.update()
        elif window.changed == "state":
            self.update()

    def mousePressEvent(self, event):
        if event.button() == 1:
            self.window.activate()
        elif event.button() == 2:
            self.window.open_menu(bottom_left=self.mapToGlobal(QPoint(0, 0)))

    def paintEvent(self, event):
        print("paintEvent")
        painter = QPainter(self)
        # painter.setRenderHints(QPainter.Antialiasing)

        # painter.
        # pen = QPen(QColor(0x0, 0x0, 0x0))
        # pen.setWidth(1)
        # painter.setPen(pen)
        # painter.setBrush(QBrush(Qt.white))
        # rect = QRect(9, 9, 8, 8)

        if self.window.is_active():
            font = painter.font()
            # font.setWeight(QFont.DemiBold)
            font.setWeight(QFont.Bold)
            painter.setFont(font)

        # painter.setBrush(QBrush(QColor(0x50, 0x50, 0x50)))
        painter.setPen(QPen(painter.background().color()))
        painter.setBrush(painter.background())
        painter.drawRect(QRect(0, 0, self.width(), self.height()))

        if self.window.is_minimized():
            painter.setPen(QPen(QColor(0x80, 0x80, 0x80)))
        else:
            painter.setPen(QPen(QColor(0xff, 0xff, 0xff)))
        painter.drawText(QRect(10, 0, self.width(), self.height()),
                         Qt.AlignVCenter, self.window.name)

        painter.setPen(QPen(painter.background().color()))
        # painter.setBrush(painter.background())
        painter.drawRect(QRect(self.width() - 10, self.height(),
                               10, self.height()))

        # painter.setPen(QPen(QColor(0xacccfb)))
        # painter.drawLine(0, 0, self.width(), 0)
        # painter.drawLine(0, 1, 0, self.height())
        #
        # painter.setPen(QPen(QColor(0x5a7cae)))
        # painter.drawLine(self.width() - 1, 0,
        #                  self.width() - 1, self.height())
        # painter.drawLine(0, self.height() - 1,
        #                  self.width(), self.height() - 1)


class TaskBarWidget(QWidget):

    def __init__(self, parent, window_handler):
        super().__init__(parent)
        self.setFixedHeight(28)
        self.window_handler = window_handler

        # self.window_mapping = {}
        self.buttons = []

        # self.setAutoFillBackground(True)
        # palette = self.palette()
        # palette.setColor(self.backgroundRole(), Qt.black)
        # self.setPalette(palette)

        # self.setAutoFillBackground(True)
        self.setStyleSheet("""
            background-color: #000000;
        """)

        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self.layout.addStretch(0)

        button = QPushButton("X", self)
        button.setFixedHeight(self.height())
        button.setFixedWidth(32)
        button.clicked.connect(self.__close_button_clicked)
        self.layout.addWidget(button)

        self.window_handler.window_added.connect(self.__window_added)
        self.window_handler.window_removed.connect(self.__window_removed)
        # self.window_handler.window_changed.connect(self.__window_changed)

    def __close_button_clicked(self):
        # parent = self
        # while parent.parentWidget():
        #     parent = parent.parentWidget()
        # parent.close()
        QApplication.instance().exit(0)

    def __button_clicked(self, button):
        button.window.activate()

    def __window_added(self, window):
        print("__window_added")
        # button = QPushButton(window.name, self)
        button = TaskBarButton(self, self.window_handler, window)

        button.window = window

        self.layout.insertWidget(len(self.buttons), button)
        self.layout.update()

        self.buttons.append(button)

    def __window_removed(self, window):
        # button = self.window_mapping[window]

        for i, button in enumerate(self.buttons):
            if button.window == window:
                break
        else:
            print("WARNING: did not find button for window", window)
            return

        del self.buttons[i]

        self.layout.removeWidget(button)
        button.disconnect()
        button.setParent(None)
        # button.destroy()
        # del self.window_mapping[window]
