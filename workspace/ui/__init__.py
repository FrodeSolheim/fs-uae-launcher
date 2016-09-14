import fsui
from fsui.qt import QObject, QSignal
from .application import Application
from .button import Button, CustomButton, FlatButton
from .canvas import Canvas
from .color import Color
from .font import Font
from .image import Image
from .image_button import ImageButton
from .image_view import ImageView
from .label import Label, MultiLineLabel
from .layout import Column, Row
from .menu import Menu
from .painter import Painter
from .panel import Panel
from .text_area import TextArea
from .text_field import TextField
from .window import Window, TitlePanel, TitleSeparator


class Object(QObject):
    pass


# noinspection PyPep8Naming
def Signal():
    return QSignal()


def screen_size():
    return fsui.get_screen_size()
