from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import weakref
from fsui.qt import QSignal, Qt, QPoint, QRect, QEvent
from fsui.qt import QWidget, QVBoxLayout, QColor, QPainter, QPen, QBrush
from fs_uae_workspace.desktop import get_root_window
from fsbc.signal import Signal


class WindowContent(QWidget):

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), QColor(0xed, 0xed, 0xed))
        # p.setColor(self.backgroundRole(), QColor(0xff, 0xaa, 0xaa))
        self.setPalette(p)


# class FSUAEDesktopWindow(QWidget):
#
#     def __init__(self, parent=None, title=""):
#         if parent is None:
#             parent = get_root_window()
#         QWidget.__init__(self, parent)
#         self.left_padding = 6
#         self.right_padding = 6
#         self.top_padding = 30
#         self.bottom_padding = 6
#
#         self.setAutoFillBackground(True)
#         p = self.palette()
#         p.setColor(self.backgroundRole(), QColor(0xff, 0xaa, 0xaa))
#         self.setPalette(p)
#
#         # self.__content = WindowContent(self)
#         # layout = QVBoxLayout()
#         # layout.addWidget(self.__content, 1)
#         # self.setLayout(layout)
#         # return self.__content
#
#     def width(self):
#         return QWidget.width(self) - self.left_padding - self.right_padding
#
#     def height(self):
#         return QWidget.height(self) - self.top_padding - self.bottom_padding
#
#     def size(self):
#         return self.width(), self.height()
#
#     def resize(self, w, h):
#         #self.SetClientSize(size)
#         #print("FIXME:\n\nDialog.set_size")
#         QWidget.resize(self, w + self.left_padding + self.right_padding,
#                        h + self.top_padding + self.bottom_padding)
#
#     # def resizeEvent(self, event):
#     #     print("resized..")
#     #     self.on_resize()

class QContent(QWidget):

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

    def mousePressEvent(self, event):
        pass

    def mouseReleaseEvent(self, event):
        pass

    def mouseMoveEvent(self, event):
        pass


class QWindow(QWidget):

    closed = QSignal()

    def __init__(self, parent=None):
        if parent is None:
            parent = get_root_window()

        self._window = weakref.ref(self)

        self.padding = [6, 26, 6, 6]

        self._position_specified = False
        self._size_specified = False

        QWidget.__init__(self, parent)
        self.setAttribute(Qt.WA_DeleteOnClose, True)
        # self.setWindowTitle(title)

        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), QColor(0x739cda))
        # p.setColor(self.backgroundRole(), QColor(0xff, 0xaa, 0xaa))
        self.setPalette(p)

        self.mouse_press_event = None

        self.w = QContent()

        self.w.setAutoFillBackground(True)
        p = self.w.palette()
        p.setColor(self.w.backgroundRole(), QColor(0xededed))
        self.w.setPalette(p)

        layout = QVBoxLayout()
        layout.setContentsMargins(*self.padding)
        layout.addWidget(self.w)
        QWidget.setLayout(self, layout)

        # self.closed = Signal()
        # self.destroyed = Signal()

        self.w.installEventFilter(self)
        # self.installEventFilter(self)

    def eventFilter(self, obj, event):
        assert isinstance(event, QEvent)
        if event.type() == QEvent.MouseButtonPress:
            self.raise_()
        return False

    def set_position(self, position):
        self.move(position[0], position[1])

    def move(self, x, y):
        QWidget.move(self, x, y)
        self._position_specified = True

    def resize(self, w, h):
        w += self.padding[0] + self.padding[2]
        h += self.padding[1] + self.padding[3]
        QWidget.resize(self, w, h)

    def show(self):
        if not self._position_specified:
            from fs_uae_workspace.shell import set_initial_window_position
            set_initial_window_position(self)
        QWidget.show(self)

    def is_shown(self):
        return self.isVisible()

    def setLayout(self, layout):
        self.w.setLayout(layout)

    def setCentralWidget(self, widget):

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(widget)
        self.w.setLayout(layout)

    def mousePressEvent(self, event):
        if True:
            self.raise_()
        # mouse is automatically grabbed by QT, as long as the mouse button
        # is pressed, so no need to grab it here.
        self.mouse_press_event = event.x(), event.y(), event.globalX(), \
                                 event.globalY()
        self.mouse_press_window_pos = self.pos()

    def mouseReleaseEvent(self, event):
        if self.mouse_press_event[0] < 26 and self.mouse_press_event[1] < \
                26 and event.x() < 26 and event.y() < 26:
            print("close")
            self.close()
        # print("mouseReleaseEvent")
        self.mouse_press_event = None

    def mouseMoveEvent(self, event):
        if self.mouse_press_event is not None:
            dx = event.globalX() - self.mouse_press_event[2]
            dy = event.globalY() - self.mouse_press_event[3]
            x = self.mouse_press_window_pos.x() + dx
            y = self.mouse_press_window_pos.y() + dy
            # self.move(QPoint(x, y))
            self.move(x, y)

    def paintEvent(self, event):
        painter = QPainter(self)
        # painter.setRenderHints(QPainter.Antialiasing)

        pen = QPen(QColor(0x0, 0x0, 0x0))
        pen.setWidth(1)
        painter.setPen(pen)
        painter.setBrush(QBrush(Qt.white))
        rect = QRect(9, 9, 8, 8)
        painter.drawRect(rect)

        painter.drawText(
            QRect(24, 0, 1000, 26), Qt.AlignVCenter, self.windowTitle())

        painter.setPen(QPen(QColor(0xacccfb)))
        painter.drawLine(0, 0, self.width(), 0)
        painter.drawLine(0, 1, 0, self.height())

        painter.setPen(QPen(QColor(0x5a7cae)))
        painter.drawLine(self.width() - 1, 0, self.width() - 1, self.height())
        painter.drawLine(0, self.height() - 1, self.width(), self.height() - 1)

    def closeEvent(self, event):
        print("Window.closeEvent")
        # for function in self.close_listeners:
        #     function()
        self.closed.emit()
        self.on_close()
        event.accept()
        #self.destroy()
         #event.ignore()

    def on_close(self):
        pass


class Window(QWindow):

    def __init__(self, parent=None, title=""):
        QWindow.__init__(self, parent)
        self.setWindowTitle(title)

        self._container = WindowContent(self)
        self.setCentralWidget(self._container)

        self.destroy_listeners = []
        self.close_listeners = []

    def get_container(self):
        return self._container

    def get_parent(self):
        return None

    def add_destroy_listener(self, function):
        self.destroy_listeners.append(function)

    def add_close_listener(self, function):
        # self.close_listeners.append(function)
        self.closed.connect(function)

    def get_window(self):
        return self

    def on_destroy(self):
        pass

    def __destroyed(self):
        print("__destroyed")
        for function in self.destroy_listeners:
            function()
        self.on_destroy()

    def showEvent(self, event):
        print("showed..")
        self.on_resize()

    def get_position(self):
        return self.pos().x(), self.pos().y()

    def get_size(self):
        w = self.width()
        h = self.height()
        w -= self.padding[0] + self.padding[2]
        h -= self.padding[1] + self.padding[3]
        return w, h

    def set_size(self, size):
        w, h = size
        self._size_specified = True
        self.resize(w, h)

    def is_maximized(self):
        #return self.isMaximized()
        print("FIXME: always returning False")
        return False

    def maximize(self):
        self.showMaximized()

    def center_on_parent(self):
        #self.CenterOnParent()
        print("FIXME:\n\nWindow.center_on_parent")

    def center_on_screen(self):
        #self.CenterOnParent()
        print("FIXME:\n\nWindow.center_on_screen")

    def resizeEvent(self, event):
        print("resized..")
        self.on_resize()

    def on_resize(self):
        if self.layout:
            self.layout.set_size(self.get_size())
            self.layout.update()

    def set_background_color(self, color):
        print("FIXME: Window.set_background_color")

    def set_icon_from_path(self, path):
        print("FIXME: Window.set_icon_from_path")

    def show(self):
        if hasattr(self, "layout") and not self._size_specified:
            self.set_size(self.layout.get_min_size())
        QWindow.show(self)
