from fsui.common.element import Element as Element
from fsui.common.element import LightElement as LightElement
from fsui.common.group import Group as Group
from fsui.common.layout import HorizontalLayout as HorizontalLayout
from fsui.common.layout import Layout as Layout
from fsui.common.layout import VerticalLayout as VerticalLayout
from fsui.common.spacer import Spacer as Spacer
from fsui.qt import Signal as Signal
from fsui.qt import get_screen_size as get_screen_size
from fsui.qt import show_error as show_error
from fsui.qt import call_after as call_after
from fsui.qt.adapter import Adapter as Adapter
from fsui.qt.Application import Application as Application
from fsui.qt.Button import Button as Button
from fsui.qt.CheckBox import CheckBox as CheckBox
from fsui.qt.CheckBox import HeadingCheckBox as HeadingCheckBox
from fsui.qt.Choice import Choice as Choice
from fsui.qt.Choice import ItemChoice as ItemChoice
from fsui.qt.Color import Color as Color
from fsui.qt.ComboBox import ComboBox as ComboBox
from fsui.qt.dialog import Dialog as Dialog
from fsui.qt.dialogbuttons import DialogButtons as DialogButtons
from fsui.qt.dialogwindow import DialogWindow as DialogWindow
from fsui.qt.DirDialog import DirDialog as DirDialog
from fsui.qt.DrawingContext import DrawingContext as DrawingContext
from fsui.qt.DrawingContext import Font as Font
from fsui.qt.FileDialog import FileDialog as FileDialog
from fsui.qt.FileDialog import pick_directory as pick_directory
from fsui.qt.FileDialog import pick_file as pick_file
from fsui.qt.FileDialog import pick_files as pick_files
from fsui.qt.HeadingLabel import HeadingLabel as HeadingLabel
from fsui.qt.Icon import Icon as Icon
from fsui.qt.Image import Image as Image
from fsui.qt.ImageButton import ImageButton as ImageButton
from fsui.qt.ImageView import ImageView as ImageView
from fsui.qt.label import Label as Label
from fsui.qt.label import MultiLineLabel as MultiLineLabel
from fsui.qt.label import PlainLabel as PlainLabel
from fsui.qt.label import URLLabel as URLLabel
from fsui.qt.legacydialog import LegacyDialog as LegacyDialog
from fsui.qt.ListView import ListView as ListView
from fsui.qt.Menu import Menu as Menu
from fsui.qt.Menu import PopupMenu as PopupMenu
from fsui.qt.Panel import Panel as Panel
from fsui.qt.scrollarea import VerticalScrollArea as VerticalScrollArea
from fsui.qt.SpinCtrl import SpinCtrl as SpinCtrl
from fsui.qt.System import System as System
from fsui.qt.TextArea import TextArea as TextArea
from fsui.qt.TextField import PasswordField as PasswordField
from fsui.qt.TextField import TextField as TextField
from fsui.qt.timer import IntervalTimer as IntervalTimer
from fsui.qt.VerticalItemView import VerticalItemView as VerticalItemView
from fsui.qt.window import Window as Window

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
