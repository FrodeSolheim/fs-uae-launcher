from fsui.common.element import Element, LightElement
from fsui.common.group import Group
from fsui.common.layout import VerticalLayout, HorizontalLayout
from fsui.common.spacer import Spacer
from fsui.qt import *
from fsui.qt.adapter import Adapter
from fsui.qt.Application import Application
from fsui.qt.Button import Button
from fsui.qt.CheckBox import CheckBox, HeadingCheckBox
from fsui.qt.Color import Color
from fsui.qt.Choice import Choice, ItemChoice
from fsui.qt.ComboBox import ComboBox
from fsui.qt.dialog import Dialog
from fsui.qt.dialogbuttons import DialogButtons
from fsui.qt.DirDialog import DirDialog
from fsui.qt.DrawingContext import DrawingContext, Font
from fsui.qt.FileDialog import FileDialog, pick_directory, pick_file, pick_files
from fsui.qt.HeadingLabel import HeadingLabel
from fsui.qt.Icon import Icon
from fsui.qt.Image import Image
from fsui.qt.ImageButton import ImageButton
from fsui.qt.ImageView import ImageView
from fsui.qt.label import Label, PlainLabel, URLLabel, MultiLineLabel
from fsui.qt.legacydialog import LegacyDialog
from fsui.qt.ListView import ListView
from fsui.qt.Menu import Menu, PopupMenu
from fsui.qt.Panel import Panel
from fsui.qt.scrollarea import VerticalScrollArea
from fsui.qt.SpinCtrl import SpinCtrl
from fsui.qt.System import System
from fsui.qt.timer import IntervalTimer
from fsui.qt.TextArea import TextArea
from fsui.qt.TextField import TextField, PasswordField
from fsui.qt.VerticalItemView import VerticalItemView
from fsui.qt.window import Window


default_window_parent = []
default_window_center = []
toolkit = "qt"
use_qt = True


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
