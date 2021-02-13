# import weakref
from fsgamesys.FSGameSystemContext import FSGameSystemContext
from fsui.context import get_window
from launcher.launcher_settings import LauncherSettings
from launcher.system.classes.theme import Theme


def get_config(widget):
    return get_gscontext(widget).config


def get_gscontext(widget) -> FSGameSystemContext:
    # return window(widget).gscontext
    # print(get_window(widget).gscontext)
    return get_window(widget).gscontext


def get_settings(widget):
    return LauncherSettings
    # return imported_app.settings
    # return window(widget).app.settings


def get_wsopen(widget):
    from launcher.system.wsopen import wsopen

    return wsopen


def app(widget):
    return window(widget).app


# FIXME: Deprecated
def config(widget):
    return gscontext(widget).config


def gscontext(widget) -> FSGameSystemContext:
    return window(widget).gscontext
    # try:
    #     return widget._cached_gscontext
    # except AttributeError:
    #     widget._cached_gscontext = window(widget).gscontext
    #     return widget._cached_gscontext


# FIXME: Replaced with fsui.get_parent?
def parent(widget):
    try:
        return widget._cached_parent
    except AttributeError:
        widget._cached_parent = widget.parent()
        return widget._cached_parent
    # return widget.parent()


# FIXME: Deprecated
def settings(widget):
    return LauncherSettings
    # return imported_app.settings
    # return window(widget).app.settings


_theme = None


# FIXME: Used by initialize_qt_style for now
def get_global_theme():
    global _theme
    if _theme is None:
        _theme = Theme()
    return _theme


def get_launcher_theme(widget):
    return get_global_theme()


# FIXME: Replaced with fsui.get_theme?
def get_theme(widget):
    return get_global_theme()


def qwidget(widget):
    return widget._widget


def qwindow(widget):
    # FIXME
    # window(widget)
    pass


# FIXME: Replaced with fsui.get_window?
def window(widget):
    try:
        return widget._cached_window
    except AttributeError:
        widget._cached_window = widget.window
        return widget._cached_window
