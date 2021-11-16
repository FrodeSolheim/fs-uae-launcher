from typing import Any, Callable, Optional

from fsui.common.i18n import gettext
from fsui.qt.core import QTimer
from fsui.qt.qparent import QOptionalParent
from fsui.qt.qt import init_qt
from fsui.qt.toplevelwidget import TopLevelWidget
from fsui.qt.widgets import QDesktopWidget, QMessageBox
from fswidgets.types import Size


def get_screen_size() -> Size:
    init_qt()
    # FIXME: QDesktopWidget is deprecated
    desktop = QDesktopWidget()
    geometry = desktop.geometry()
    size = geometry.width(), geometry.height()
    print("using screen size", size)
    return size


def callLater(duration: float, function: Callable[[], None]) -> None:
    call_later(round(duration * 1000), function)


def call_later(
    duration: int, function: Callable[..., None], *args: Any, **kwargs: Any
) -> None:
    # print("FIXME: call_later", duration, function)
    # raise NotImplementedError()
    # QApplication.instance().
    def timer_callback() -> None:
        function(*args, **kwargs)

    QTimer.singleShot(duration, timer_callback)


def show_error(
    message: str,
    title: Optional[str] = None,
    parent: Optional[TopLevelWidget] = None,
) -> None:
    if title is None:
        title = gettext("An Error Occurred")
    # QErrorMessage().showMessage(message)
    # message_box = QMessageBox()
    # message_box.setIcon(QMessageBox.Critical)
    # message_box.setText(message)
    # message_box.exec_()
    QMessageBox.critical(QOptionalParent(parent), title, message)


def show_warning(
    message: str,
    title: Optional[str] = None,
    parent: Optional[TopLevelWidget] = None,
) -> None:
    if title is None:
        title = gettext("Warning")
    QMessageBox.warning(QOptionalParent(parent), title, message)


def error_function(title: str) -> Callable[[str], None]:
    def error_function_2(message: str) -> None:
        show_error(message, title)

    return error_function_2
