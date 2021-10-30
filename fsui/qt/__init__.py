import queue
import traceback
from typing import Any, Callable

from fsui.qt.qparent import QParent
from fsui.qt.qt import *

# pylint: disable=no-name-in-module
# noinspection PyUnresolvedReferences
from fsui.qt.qt import (
    init_qt,
    QCheckBox,
    QColor,
    QColorDialog,
    QComboBox,
    QCoreApplication,
    QCursor,
    QDesktopWidget,
    QDialog,
    QEvent,
    QFileDialog,
    QFont,
    QFontDatabase,
    QFontMetrics,
    QFrame,
    QGLWidget,
    QIcon,
    QImage,
    QLineEdit,
    QMessageBox,
    QObject,
    QPixmap,
    QPushButton,
    QSize,
    QSpinBox,
    QSvgRenderer,
    QTextCursor,
    QTextEdit,
    QTimer,
    Qt,
    QWidget,
)
from fsui.res import gettext


def get_screen_size():
    init_qt()
    desktop = QDesktopWidget()
    geometry = desktop.geometry()
    size = geometry.width(), geometry.height()
    print("using screen size", size)
    return size


def callLater(duration: float, function: Callable[[], None]):
    call_later(round(duration * 1000), function)


def call_later(
    duration: int, function: Callable[..., None], *args: Any, **kwargs: Any
):
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


from fsui.qt.callafter import call_after
