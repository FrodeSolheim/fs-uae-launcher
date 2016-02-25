import traceback
import queue

from fsui.res import gettext
from .qt import *
from .helpers import QParent


def get_screen_size():
    init_qt()
    desktop = QDesktopWidget()
    geometry = desktop.geometry()
    size = geometry.width(), geometry.height()
    print("using screen size", size)
    return size


def get_mouse_position():
    # noinspection PyArgumentList
    pos = QCursor.pos()
    return pos.x(), pos.y()


class CustomEvent(QEvent):
    
    def __init__(self):
        QEvent.__init__(self, QEvent.User)


class EventHandler(QObject):

    def __init__(self):
        QObject.__init__(self)
        self.queue = queue.Queue()

    def customEvent(self, event):
        while True:
            try:
                function, args, kwargs = self.queue.get_nowait()
            except queue.Empty:
                break
            try:
                function(*args, **kwargs)
            except Exception:
                # log.warn("callback event failed: %r %r",
                #         self.callback, self.args, exc_info=True)
                print("-- callback exception --")
                traceback.print_exc()

    def post_callback(self, function, *args, **kwargs):
        self.queue.put((function, args, kwargs))
        QCoreApplication.instance().postEvent(self, CustomEvent())

event_handler = EventHandler()


def call_after(function, *args, **kwargs):
    event_handler.post_callback(function, *args, **kwargs)


def call_later(duration, function, *args, **kwargs):
    # print("FIXME: call_later", duration, function)
    # raise NotImplementedError()
    # QApplication.instance().
    def timer_callback():
        function(*args, **kwargs)
    QTimer.singleShot(duration, timer_callback)


def show_error(message, title=None, parent=None):
    if not title:
        title = gettext("An Error Occurred")
    # QErrorMessage().showMessage(message)
    # message_box = QMessageBox()
    # message_box.setIcon(QMessageBox.Critical)
    # message_box.setText(message)
    # message_box.exec_()
    QMessageBox.critical(QParent(parent), title, message)


def show_warning(message, title=None, parent=None):
    if not title:
        title = gettext("Warning")
    QMessageBox.warning(QParent(parent), title, message)


def error_function(title):
    def error_function_2(message):
        show_error(message, title)
    return error_function_2
