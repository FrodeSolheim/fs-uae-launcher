import weakref
from .common.element import Element, LightElement
from .common.group import Group
from .common.layout import VerticalLayout, HorizontalLayout
from .common.spacer import Spacer
from .qt import *
from .qt.adapter import Adapter
from .qt.Application import Application
from .qt.Button import Button
from .qt.CheckBox import CheckBox, HeadingCheckBox
from .qt.Color import Color
from .qt.Choice import Choice, ItemChoice
from .qt.ComboBox import ComboBox
from .qt.dialog import Dialog
from .qt.dialogbuttons import DialogButtons
from .qt.DirDialog import DirDialog
from .qt.DrawingContext import DrawingContext, Font
from .qt.FileDialog import FileDialog, pick_directory, pick_file, pick_files
from .qt.HeadingLabel import HeadingLabel
from .qt.Icon import Icon
from .qt.Image import Image
from .qt.ImageButton import ImageButton
from .qt.ImageView import ImageView
from .qt.label import Label, PlainLabel, URLLabel, MultiLineLabel
from .qt.legacydialog import LegacyDialog
from .qt.ListView import ListView
from .qt.Menu import Menu, PopupMenu
from .qt.Panel import Panel
from .qt.scrollarea import VerticalScrollArea
from .qt.SpinCtrl import SpinCtrl
from .qt.System import System
from .qt.timer import IntervalTimer
from .qt.TextArea import TextArea
from .qt.TextField import TextField, PasswordField
from .qt.VerticalItemView import VerticalItemView
from .qt.window import Window


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
        return
    cls._window_instance = cls(parent)

    def reset_instance():
        print("SettingsDialog.reset_instance")
        # cls._window_instance.deleteLater()
        cls._window_instance = None

    cls._window_instance.closed.connect(reset_instance)
    cls._window_instance.show()

    def monitor_instance_2(count):
        if count < 100:
            call_after(monitor_instance_2, count + 1)
            return
        print("DESTROYED SIGNAL RECEIVED 2")
        instance = weak_instance()
        if instance is not None:
            print("WARNING: SettingsDialog is still alive")
            import gc
            print(gc.get_referrers(instance))
            print("real window:")
            print(gc.get_referrers(instance.real_window()))
        else:
            print("Instance is now", instance)

    def monitor_instance():
        print("DESTROYED SIGNAL RECEIVED")
        call_after(monitor_instance_2, 1)

    weak_instance = weakref.ref(cls._window_instance)
    # cls._window_instance.destroyed.connect(monitor_instance)
    cls._window_instance.closed.connect(monitor_instance)

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
