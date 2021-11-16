from typing import Optional

from fsui.qt.toplevelwidget import TopLevelWidget
from fsui.theme import Theme
from fswidgets.widget import Widget

default_theme = Theme()


def get_parent(widget: Widget) -> Optional[Widget]:
    try:
        return widget.internalCachedParent
    except AttributeError:
        widget.internalCachedParent = widget.parent()
        return widget.internalCachedParent


def get_window(widget: Widget) -> TopLevelWidget:
    # print("get_window", widget)
    # import traceback
    # traceback.print_stack()
    # print("get_window", widget, widget.__dict__)
    try:
        return widget.internalCachedWindow
    except AttributeError:
        # print("THEME - GET WINDOW", widget)
        # print(f" - {widget}")
        w = widget
        while w.hasParent():
            # print("- THEME - PARENT", widget)
            w = w.getParent()
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
        assert isinstance(w, TopLevelWidget)
        widget.internalCachedWindow = w
        return widget.internalCachedWindow


def get_theme(widget: Widget) -> Theme:
    window = get_window(widget)
    assert isinstance(window, TopLevelWidget)
    # assert window is not None
    if hasattr(window, "theme"):
        theme = window.theme
        assert isinstance(theme, Theme)
        return theme
    else:
        return default_theme
