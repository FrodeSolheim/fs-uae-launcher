from fsui.qt.qt import QCursor
from fswidgets.types import Point


def get_mouse_position() -> Point:
    # noinspection PyArgumentList
    pos = QCursor.pos()
    return pos.x(), pos.y()
