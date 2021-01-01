from fsui.theme import Theme

default_theme = Theme()


def get_parent(widget):
    try:
        return widget._cached_parent
    except AttributeError:
        widget._cached_parent = widget.parent()
        return widget._cached_parent


def get_window(widget):
    # print("get_window", widget)
    # import traceback
    # traceback.print_stack()
    # print("get_window", widget, widget.__dict__)
    try:
        return widget._cached_window
    except AttributeError:
        # print("THEME - GET WINDOW", widget)
        # print(f" - {widget}")
        w = widget
        while w.parent():
            # print("- THEME - PARENT", widget)
            w = w.parent()
            # print(f" - {w}")

            # If we get to a real QMainWindow parent, we want instead to get
            # the fsui wrapper. This can happen if we traverse the parent
            # chain when using widgets directly inheriting from Qt widgets.
            #  FIXME: The fsui widget hierarchy is a mess at
            # the moment - clean up?
            # if hasattr(widget, "fake_window"):
            #     widget = widget.fake_window()
            #     # print("- THEME - PARENT (FAKE)", widget)

            # try:
            #     print(widget._fswidget)
            # except AttributeError:
            #     # print("hasn't got _fswidget")

            # if hasattr(widget, "_fswidget_ref"):
            #     # print("has widget ref")

            if hasattr(w, "_fswidget"):
                w = w._fswidget
                break
                # print(f" - (->fs) {widget}")
            # print(widget)
            # print(widget.__dict__)

        # print("- THEME - WINDOW =", widget)
        # print("- THEME - THEME =", widget.theme)
        # print("cache ->", w)
        widget._cached_window = w
        return widget._cached_window


def get_theme(widget):
    window = get_window(widget)
    # print("get_theme window is", window)
    try:
        return window.theme
    except AttributeError:
        return default_theme
