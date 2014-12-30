import sys
from fsbc.Application import app
from fsui.qt import Qt, QMainWindow, QGLWidget, QKeyEvent
from game_center.glui.input import InputHandler
from .event import Event


# noinspection PyPep8Naming
class GLWidget(QGLWidget):

    def __init__(self, parent, callbacks):
        QGLWidget.__init__(self, parent)
        set_black_background(self)
        self._callbacks = callbacks
        self._initialized = False

        palette = self.palette()
        palette.setColor(self.backgroundRole(), Qt.blue)
        self.setPalette(palette)
        self.setAutoFillBackground(True)
        self.setStyleSheet("background-color: black;")

    def initializeGL(self):
        print("GLWidget.initializeGL")
        # moved initialization to resizeGL due to issues on OS X

    def resizeGL(self, width, height):
        print("GLWidget.resizeGL", width, height)
        if not self._initialized:
            if width == 160 and height == 160:
                # work around bug(?) on os x
                return
            self._callbacks.initialize()
            self._initialized = True
        self._callbacks.resize(width, height)

    def paintGL(self):
        self._callbacks.render()


# noinspection PyPep8Naming
class QtWindow(QMainWindow):

    def __init__(self, callback, interval):
        # QMainWindow.__init__(self, None, Qt.X11BypassWindowManagerHint)
        QMainWindow.__init__(self)
        set_black_background(self)
        if app.name == "fs-uae-arcade":
            self.setWindowTitle("FS-UAE Arcade")
        else:
            self.setWindowTitle("FS Game Center")
        self.gl_widget = GLWidget(self, callback)
        if not "--show-cursor" in sys.argv:
            self.setCursor(Qt.BlankCursor)
            self.gl_widget.setCursor(Qt.BlankCursor)
        self.setCentralWidget(self.gl_widget)
        self.startTimer(interval)
        self.callback = callback
        # self.resize(940, 540)

    def restore_window_if_necessary(self):
        pass
        # print("restore_window_if_necessary")
        # print("is minimized:", self.isMinimized())
        # # under Gnome 3, the window is minized when launching FS-UAE
        # # full-screen from full-screen arcade/game center.
        # if self.isMinimized():
        #     # self.showFullScreen()
        #     self.setWindowState(self.windowState() ^ Qt.WindowMinimized)
        #     self.activateWindow()

    def timerEvent(self, event):
        self.callback.timer()
        self.gl_widget.updateGL()
        # self.callback()

    def keyPressEvent(self, event):
        assert isinstance(event, QKeyEvent)
        # print(event.isAutoRepeat(), event.type())
        if event.isAutoRepeat():
            return
        InputHandler.add_event(Event.create_key_event(event))
        text = event.text()
        if text and text in TEXT_WHITE_LIST:
            # We don't want special characters such as return, backspace
            # and escape (etc) to be sent as text events. For now, we use
            # a simple white list.
            InputHandler.add_event({
                "type": "text",
                "text": event.text(),
            })

    def keyReleaseEvent(self, event):
        assert isinstance(event, QKeyEvent)
        # print(QKeyEvent, event.isAutoRepeat(), event.type())
        if event.isAutoRepeat():
            return
        InputHandler.add_event(Event.create_key_event(event))


TEXT_WHITE_LIST = (
    "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.,- ")


def set_black_background(widget):
    palette = widget.palette()
    palette.setColor(widget.backgroundRole(), Qt.blue)
    widget.setPalette(palette)
    widget.setAutoFillBackground(True)
    widget.setStyleSheet("background-color: black;")
