import weakref

from fsui.qt.callafter import call_after
from fsui.qt.qparent import QParent
from fsui.qt.qt import QFrame, QScrollArea, Qt
from fswidgets.widget import Widget


# noinspection PyProtectedMember
class QScrollAreaWrapper(QScrollArea):
    def __init__(self, parent, *, owner):
        super().__init__(parent)
        self._owner = owner

    # FIXME: Needed?
    def owner(self):
        return self._owner

    # FIXME: Needed? Move to Widget?
    def resizeEvent(self, event):
        self.owner().on_resize()


class ScrollArea(Widget):
    def __init__(self, parent):
        super().__init__(
            parent, QScrollAreaWrapper(QParent(parent), owner=self)
        )
        self._qwidget.move(0, 2000)

        self._parent = weakref.ref(parent)
        # QWidget.__init__(self, QParent(parent))
        # self.init_widget(parent)
        self.layout = None
        self._painter = None

        # QScrollArea.__init__(self, parent.get_container())
        # self.init_widget(parent)
        self.__child = None
        # self.layout = None
        # self._painter = None

        # self._qwidget.move(0, 2000)

        # self.set_background_color(Color(0xff0000))

        # Needed to make the scroll area transparent (background shows
        # through).
        self._qwidget.viewport().setAutoFillBackground(False)

        self._qwidget.setFrameShape(QFrame.NoFrame)
        self._qwidget.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self._qwidget.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

    def get_child(self):
        # child = self.__child()
        # return child
        return self.__child

    def get_min_width(self):
        return self.get_child().get_min_width()

    def on_resize(self):
        child = self.get_child()
        width = self._qwidget.viewport().width()
        height = child.get_min_height(width)
        child.set_size((width, height))

    # @property
    # def size(self):
    #     return self.get_size()

    def resizeEvent(self, event):
        QScrollArea.resizeEvent(self, event)
        self.on_resize()

    def set_child(self, child):
        # self.__child = weakref.ref(child)
        self.__child = child
        widget = child.widget()
        self._qwidget.setWidget(widget)
        widget.move(0, 0)
        self.on_resize()

    def showEvent(self, event):
        self.on_resize()


# FIXME Interit from ScrollArea?


class VerticalScrollArea(Widget):
    def __init__(self, parent):
        super().__init__(parent, QScrollArea(QParent(parent)))
        self.__child = None
        # self.layout = None
        # self._painter = None

        self._qwidget.move(0, 2000)
        self._qwidget.setFrameShape(QFrame.NoFrame)
        self._qwidget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    def get_child(self):
        return self.__child

    def get_min_width(self):
        return self.get_child().get_min_width()

    def on_resize(self):
        # FIXME: Problem, probably because on_resize is called to soon (due)
        # to the event filter, and the viewport hasn't gotten its real size
        # yet. It would be better if on_resize was called from the QWidget's
        # resizeEvent handler instead of event filter... -but quick workaround
        # is to postpone handling until event handler has ended.
        # FIXME: Problem can be observed with ConfigScrollArea.
        call_after(self.on_resize_2)

    def on_resize_2(self):
        print(
            "\n\nVerticalScrollArea.on_resize",
            self.size(),
            self._qwidget.viewport().width(),
            "\n",
        )
        child = self.get_child()
        height = child.get_min_height()
        child.set_size((self._qwidget.viewport().width(), height))

    # FIXME: Resizeevent not working ATM!
    # def resizeEvent(self, event):
    #     QScrollArea.resizeEvent(self, event)
    #     self.on_resize()

    # FIXME: Showevent not working ATM!
    # def showEvent(self, event):
    #     self.on_resize()

    def set_widget(self, child):
        # self.__child = weakref.ref(child)
        self.__child = child
        child_widget = child.widget()
        self._qwidget.setWidget(child_widget)
        child_widget.move(0, 0)
        self.on_resize()
