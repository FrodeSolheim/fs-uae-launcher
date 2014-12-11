from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import traceback
import fsbc.queue
from fsui.res import gettext
from .qt import *


def get_screen_size():
    desktop = QDesktopWidget()
    geometry = desktop.geometry()
    size = geometry.width(), geometry.height()
    print("using screen size", size)
    return size


class CustomEvent(QEvent):
    
    def __init__(self):
        QEvent.__init__(self, QEvent.User)


class EventHandler(QObject):

    def __init__(self):
        QObject.__init__(self)
        self.queue = fsbc.queue.Queue()

    def customEvent(self, event):
        while True:
            try:
                function, args, kwargs = self.queue.get_nowait()
            except fsbc.queue.Empty:
                break
            try:
                function(*args, **kwargs)
            except Exception:
                #log.warn("callback event failed: %r %r",
                #        self.callback, self.args, exc_info=True)
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
    #QErrorMessage().showMessage(message)
    # message_box = QMessageBox()
    # message_box.setIcon(QMessageBox.Critical)
    # message_box.setText(message)
    # message_box.exec_()
    QMessageBox.critical(parent, title, message)


def error_function(title):
    def error_function_2(message):
        show_error(message, title)
    return error_function_2
