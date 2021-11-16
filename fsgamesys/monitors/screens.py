from typing import Dict, List, Tuple

# FIXME: Move qt code to fswidgets
from fswidgets.qt.core import QRect

# FIXME: Use a Rect dataclass instead?
ScreenRect = Dict[str, int]


def screen_rects() -> List[ScreenRect]:
    # FIXME: Move qt code to fswidgets
    screens: List[Tuple[int, ScreenRect]] = []
    try:
        from fsui.qt import init_qt

        qApplication = init_qt()
    except AttributeError:
        pass
    else:
        for screen in qApplication.screens():
            geometry = screen.geometry()  # type: QRect
            screen: ScreenRect = {
                "x": geometry.x(),
                "y": geometry.y(),
                "w": geometry.width(),
                "h": geometry.height(),
            }
            screens.append((screen["x"], screen))
    # Sort screens by x coordinate
    screens.sort()
    return [screen[1] for screen in screens]
