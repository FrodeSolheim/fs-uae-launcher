import weakref
from fsui.qt import Qt, QScrollArea, QFrame
from .widget_mixin import WidgetMixin


class VerticalScrollArea(QScrollArea, WidgetMixin):

    def __init__(self, parent):
        QScrollArea.__init__(self, parent.get_container())
        self.init_widget(parent)
        self.__child = None
        # self.layout = None
        # self._painter = None

        self.move(0, 2000)
        # self.setAutoFillBackground(True)
        self.setFrameShape(QFrame.NoFrame)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    @property
    def size(self):
        return self.get_size()

    def showEvent(self, event):
        self.on_resize()

    def resizeEvent(self, event):
        QScrollArea.resizeEvent(self, event)
        self.on_resize()

    def get_child(self):
        # child = self.__child()
        # return child
        return self.__child

    def get_min_width(self):
        return self.get_child().get_min_width()

    def on_resize(self):
        child = self.get_child()
        height = child.get_min_height()
        child.set_size((self.viewport().width(), height))

    def set_widget(self, child):
        # self.__child = weakref.ref(child)
        self.__child = child
        widget = child.widget()
        self.setWidget(widget)
        widget.move(0, 0)
        self.on_resize()
