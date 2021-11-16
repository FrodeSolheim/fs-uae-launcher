from typing import List

from fsui.common.group import Group
from fsui.common.layout import HorizontalLayout, Layout, VerticalLayout
from fsui.common.spacer import Spacer
from fsui.context import get_parent, get_theme, get_window
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
from fsui.qt.toplevelwidget import TopLevelWidget
from fsui.qt.verticalitemview import VerticalItemView
from fsui.qt.window import Window
from fsui.util import current_window_instance, open_window_instance
from fswidgets.checkbox import CheckBox
from fswidgets.types import Position
from fswidgets.widget import Widget

default_window_parent: List[TopLevelWidget] = []
default_window_center: List[Position] = []
toolkit = "qt"
use_qt = True
theme = ""
theme_variant = ""

from fsui.common.element import Element, LightElement
