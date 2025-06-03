import fsui
from fsui.qt import QObject, QSignal

from .application import Application as Application
from .button import Button as Button
from .button import CustomButton as CustomButton
from .button import FlatButton as FlatButton
from .canvas import Canvas as Canvas
from .color import Color as Color
from .font import Font as Font
from .image import Image as Image
from .image_button import ImageButton as ImageButton
from .image_view import ImageView as ImageView
from .label import Label as Label
from .label import MultiLineLabel as MultiLineLabel
from .layout import Column as Column
from .layout import Row as Row
from .menu import Menu as Menu
from .painter import Painter as Painter
from .panel import Panel as Panel
from .text_area import TextArea as TextArea
from .text_field import TextField as TextField
from .window import TitlePanel as TitlePanel
from .window import TitleSeparator as TitleSeparator
from .window import Window as Window


class Object(QObject):
    pass


# noinspection PyPep8Naming
def Signal():
    return QSignal()


def screen_size():
    return fsui.get_screen_size()
