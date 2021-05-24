from fsui.common.element import Element, LightElement
from fsui.common.group import Group
from fsui.common.layout import HorizontalLayout, Layout, VerticalLayout
from fsui.common.spacer import Spacer
from fsui.qt import *
from fsui.qt.adapter import Adapter
from fsui.qt.Application import Application
from fsui.qt.button import Button
from fsui.qt.choice import Choice, ItemChoice
from fsui.qt.color import Color
from fsui.qt.combobox import ComboBox
from fsui.qt.dialog import Dialog
from fsui.qt.dialogbuttons import DialogButtons
from fsui.qt.dialogwindow import DialogWindow
from fsui.qt.dirdialog import DirDialog
from fsui.qt.drawingcontext import DrawingContext
from fsui.qt.filedialog import (
    FileDialog,
    pick_directory,
    pick_file,
    pick_files,
)
from fsui.qt.font import Font
from fsui.qt.headinglabel import HeadingLabel
from fsui.qt.icon import Icon
from fsui.qt.image import Image
from fsui.qt.imagebutton import ImageButton
from fsui.qt.imageview import ImageView
from fsui.qt.label import Label, MultiLineLabel, PlainLabel, URLLabel
from fsui.qt.legacydialog import LegacyDialog
from fsui.qt.listview import ListView
from fsui.qt.menu import Menu, PopupMenu
from fsui.qt.mouse import get_mouse_position
from fsui.qt.panel import Panel
from fsui.qt.scrollarea import ScrollArea, VerticalScrollArea
from fsui.qt.signal import Signal
from fsui.qt.spinctrl import SpinCtrl
from fsui.qt.system import System
from fsui.qt.textarea import TextArea
from fsui.qt.textfield import PasswordField, TextField
from fsui.qt.timer import IntervalTimer
from fsui.qt.verticalitemview import VerticalItemView
from fsui.qt.window import Window
from fswidgets.checkbox import CheckBox
from fswidgets.widget import Widget

default_window_parent = []
default_window_center = []
toolkit = "qt"
use_qt = True
theme = ""
theme_variant = ""


# noinspection PyProtectedMember
def open_window_instance(cls, parent=None):
    if not hasattr(cls, "_window_instance"):
        cls._window_instance = None
    if cls._window_instance is not None:
        cls._window_instance.raise_and_activate()
        return cls._window_instance
    cls._window_instance = cls(parent)

    def reset_instance():
        print("SettingsDialog.reset_instance")
        # cls._window_instance.deleteLater()
        cls._window_instance = None

    cls._window_instance.closed.connect(reset_instance)
    cls._window_instance.show()
    return cls._window_instance

    # def monitor_instance_2(count):
    #     if count < 100:
    #         call_after(monitor_instance_2, count + 1)
    #         return
    #     print("DESTROYED SIGNAL RECEIVED 2")
    #     instance = weak_instance()
    #     if instance is not None:
    #         print("WARNING: SettingsDialog is still alive")
    #         import gc
    #         print(gc.get_referrers(instance))
    #         print("real window:")
    #         print(gc.get_referrers(instance.real_window()))
    #     else:
    #         print("Instance is now", instance)
    #
    # def monitor_instance():
    #     print("DESTROYED SIGNAL RECEIVED")
    #     call_after(monitor_instance_2, 1)
    #
    # weak_instance = weakref.ref(cls._window_instance)
    # # cls._window_instance.destroyed.connect(monitor_instance)
    # cls._window_instance.closed.connect(monitor_instance)

    # if getattr(cls, "_window_instance", None) and cls._window_instance():
    #     cls._window_instance().raise_and_activate()
    # else:
    #     window = cls(parent)
    #     window.show()
    #     cls._window_instance = weakref.ref(window)


# noinspection PyProtectedMember
def current_window_instance(cls):
    if not hasattr(cls, "_window_instance"):
        return None
    return cls._window_instance


# def get_parent(widget):
#     try:
#         return widget._cached_parent
#     except AttributeError:
#         widget._cached_parent = widget.parent()
#         return widget._cached_parent


# def get_window(widget):
#     try:
#         return widget._cached_window
#     except AttributeError:
#         widget._cached_window = widget.window
#         return widget._cached_window


# from fsui.theme import Theme
# default_theme = Theme()


# def get_theme(widget):
#     try:
#         return get_window(widget).theme
#     except AttributeError:
#         return default_theme
from fsui.context import get_parent, get_theme, get_window
