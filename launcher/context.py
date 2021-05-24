# import weakref
from typing import Optional, cast

from fsgamesys.FSGameSystemContext import FSGameSystemContext
from fsui.context import get_window
from fswidgets.parentstack import ParentStack
from fswidgets.widget import Widget
from launcher.i18n import gettext
from launcher.launcher_settings import LauncherSettings
from launcher.settings.launchersettings2 import LauncherSettings2
from system.classes.theme import Theme


def useImageLoader(widget: Optional[Widget] = None):
    return useLauncherWindow(widget).imageLoader


def useInputService():
    from fsgamesys.input2.inputservice import InputService

    return InputService.getInstance()


def useLauncherWindow(widget: Optional[Widget] = None):
    widget = widget or ParentStack.top()
    from launcher.ui2.launcher2window import Launcher2Window

    return cast(Launcher2Window, widget.getWindow())


def useSettings():
    return LauncherSettings2()


def useTranslation():
    return gettext


# -----------------------------------------------------------------------------


def get_config(widget: Widget):
    return get_gscontext(widget).config


def get_gscontext(widget: Widget) -> FSGameSystemContext:
    # return window(widget).gscontext
    # print(get_window(widget).gscontext)
    return get_window(widget).gscontext


def get_settings(widget: Widget):
    return LauncherSettings
    # return imported_app.settings
    # return window(widget).app.settings


def get_wsopen(widget: Widget):
    from system.wsopen import wsopen

    return wsopen


def app(widget: Widget):
    return window(widget).app


# FIXME: Deprecated
def config(widget: Widget):
    return gscontext(widget).config


def gscontext(widget: Widget) -> FSGameSystemContext:
    return window(widget).gscontext
    # try:
    #     return widget._cached_gscontext
    # except AttributeError:
    #     widget._cached_gscontext = window(widget).gscontext
    #     return widget._cached_gscontext


# FIXME: Replaced with fsui.get_parent?
def parent(widget: Widget):
    try:
        return widget._cached_parent
    except AttributeError:
        widget._cached_parent = widget.parent()
        return widget._cached_parent
    # return widget.parent()


# FIXME: Deprecated
def settings(widget: Widget):
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


def get_launcher_theme(widget: Widget):
    return get_global_theme()


# FIXME: Replaced with fsui.get_theme?
def get_theme(widget: Widget):
    return get_global_theme()


def qwidget(widget: Widget):
    return widget._widget


def qwindow(widget: Widget):
    # FIXME
    # window(widget)
    pass


# FIXME: Replaced with fsui.get_window?
def window(widget: Widget):
    try:
        return widget._cached_window
    except AttributeError:
        widget._cached_window = widget.window
        return widget._cached_window
