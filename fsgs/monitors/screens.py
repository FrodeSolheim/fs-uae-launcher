def screen_rects():
    # FIXME: Move qt code to fsui
    screens = []
    try:
        from fsui.qt import init_qt

        qapplication = init_qt()
    except AttributeError:
        pass
    else:
        for screen in qapplication.screens():
            geometry = screen.geometry()
            screen = {
                "x": geometry.x(),
                "y": geometry.y(),
                "w": geometry.width(),
                "h": geometry.height(),
            }
            screens.append((screen["x"], screen))
    # Sort screens by x coordinate
    screens.sort()
    return [screen[1] for screen in screens]
