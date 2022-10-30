import weakref

from PyQt6.QtWidgets import QWidget

from fscore.deprecated import deprecated
from fsui.qt import QObject
from fsui.qt.toplevelwidget import TopLevelWidget
from fswidgets.types import Point, Size
from fswidgets.widget import Widget


def dummy() -> None:
    # Hack to prevent import below from being moved up
    pass


# Need to import layout after fswidgets.widget here
from fsui.common.layout import Layout

# pyright: reportPrivateUsage=false

# Inheriting from QObject in order to be able to have signals associated
# with subclasses of Group.


class Group(QObject):
    def __init__(self, parent: Widget):
        super().__init__()
        self._parent = weakref.ref(parent)
        if hasattr(parent, "_window"):
            # noinspection PyProtectedMember
            self._window = parent._window
        self.layout: Layout
        self.position = (0, 0)
        self.__visible = True

    # @property
    def parent(self) -> Widget:
        widget = self._parent()
        assert widget is not None
        return widget

    # def show_or_hide(self, show):
    #     self.__visible = show

    @deprecated
    def is_visible(self) -> bool:
        return self.visible()

    def onDestroy(self) -> None:
        pass

    def get_window(self) -> TopLevelWidget:
        window = self.parent().getWindow()
        assert isinstance(window, TopLevelWidget)
        return window

    def get_container(self) -> QWidget:
        return self.parent().get_container()

    def get_min_width(self) -> int:
        return self.layout.get_min_width()

    def get_min_height(self, width: int) -> int:
        return self.layout.get_min_height(width)

    def set_position(self, position: Point) -> None:
        self.position = position
        if self.layout:
            self.layout.set_position(position)

    def set_size(self, size: Size) -> None:
        if self.layout:
            self.layout.set_size(size)

    def set_position_and_size(self, position: Point, size: Size) -> None:
        self.position = position
        if self.layout:
            self.layout.set_position_and_size(position, size)

    def visible(self) -> bool:
        return self.__visible
