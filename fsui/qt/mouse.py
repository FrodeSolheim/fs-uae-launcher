from fsui.qt.qt import QCursor


def get_mouse_position():
    # noinspection PyArgumentList
    pos = QCursor.pos()
    return pos.x(), pos.y()
