import weakref
from typing import Optional, cast

from PyQt5.QtGui import QResizeEvent
from typing_extensions import Protocol

from fsui.qt.callafter import call_after
from fsui.qt.qparent import QParent
from fsui.qt.qt import QFrame, QScrollArea, Qt
from fsui.qt.widgets import QWidget
from fswidgets.widget import Widget


class HasOnResize(Protocol):
    def on_resize(self) -> None:
        ...


# noinspection PyProtectedMember
class QScrollAreaWrapper(QScrollArea):
    def __init__(self, parent: QWidget, *, owner: HasOnResize):
        super().__init__(parent)
        self._owner = owner

    # FIXME: Needed?
    def owner(self) -> HasOnResize:
        return self._owner

    # FIXME: Needed? Move to Widget?
    def resizeEvent(self, a0: QResizeEvent) -> None:
        self.owner().on_resize()


class ScrollArea(Widget):
    def __init__(self, parent: Widget):
        super().__init__(
            parent, QScrollAreaWrapper(QParent(parent), owner=self)
        )
        self.qScrollArea.move(0, 2000)

        self._parent = weakref.ref(parent)
        # QWidget.__init__(self, QParent(parent))
        # self.init_widget(parent)
        self.layout = None
        self._painter = None

        # QScrollArea.__init__(self, parent.get_container())
        # self.init_widget(parent)
        self.__child: Optional[Widget] = None
        # self.layout = None
        # self._painter = None

        # self._qwidget.move(0, 2000)

        # self.set_background_color(Color(0xff0000))

        # Needed to make the scroll area transparent (background shows
        # through).
        self.qScrollArea.viewport().setAutoFillBackground(False)

        self.qScrollArea.setFrameShape(QFrame.NoFrame)
        self.qScrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.qScrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

    def get_child(self) -> Optional[Widget]:
        # child = self.__child()
        # return child
        return self.__child

    def get_min_width(self) -> int:
        child = self.get_child()
        if child is not None:
            return child.get_min_width()
        return 0

    def on_resize(self) -> None:
        width = self.qScrollArea.viewport().width()
        child = self.get_child()
        if child is not None:
            height = child.get_min_height(width)
            child.set_size((width, height))

    # @property
    # def size(self):
    #     return self.get_size()

    @property
    def qScrollArea(self) -> QScrollArea:
        return cast(QScrollArea, self._qwidget)

    def set_child(self, child: Widget) -> None:
        # self.__child = weakref.ref(child)
        self.__child = child
        widget = child.widget()
        self.qScrollArea.setWidget(widget)
        widget.move(0, 0)
        self.on_resize()

    # def showEvent(self, event: QShowEvent):
    #     self.on_resize()


# FIXME Interit from ScrollArea?


class VerticalScrollArea(Widget):
    def __init__(self, parent: Widget):
        super().__init__(parent, QScrollArea(QParent(parent)))
        self.__child: Optional[Widget] = None
        # self.layout = None
        # self._painter = None

        self.qScrollArea.move(0, 2000)
        self.qScrollArea.setFrameShape(QFrame.NoFrame)
        self.qScrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    def get_child(self) -> Optional[Widget]:
        return self.__child

    def get_min_width(self) -> int:
        child = self.get_child()
        if child is not None:
            return child.get_min_width()
        return 0

    def on_resize(self) -> None:
        # FIXME: Problem, probably because on_resize is called to soon (due)
        # to the event filter, and the viewport hasn't gotten its real size
        # yet. It would be better if on_resize was called from the QWidget's
        # resizeEvent handler instead of event filter... -but quick workaround
        # is to postpone handling until event handler has ended.
        # FIXME: Problem can be observed with ConfigScrollArea.
        call_after(self.on_resize_2)

    def on_resize_2(self) -> None:
        print(
            "\n\nVerticalScrollArea.on_resize",
            self.size(),
            self.qScrollArea.viewport().width(),
            "\n",
        )
        width = self.qScrollArea.viewport().width()
        child = self.get_child()
        if child is not None:
            height = child.get_min_height(width)
            child.set_size((width, height))

    # FIXME: Resizeevent not working ATM!
    # def resizeEvent(self, event):
    #     QScrollArea.resizeEvent(self, event)
    #     self.on_resize()

    # FIXME: Showevent not working ATM!
    # def showEvent(self, event):
    #     self.on_resize()

    @property
    def qScrollArea(self) -> QScrollArea:
        return cast(QScrollArea, self._qwidget)

    # FIXME: Other class as set_child
    def set_widget(self, child: Widget) -> None:
        # self.__child = weakref.ref(child)
        self.__child = child
        child_widget = child.widget()
        self.qScrollArea.setWidget(child_widget)
        child_widget.move(0, 0)
        self.on_resize()
