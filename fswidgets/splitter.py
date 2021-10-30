import traceback
import weakref
from typing import List, Optional, cast

from typing_extensions import Literal

import fsui
from fsbc.util import unused
from fsui import Widget
from fsui.common.layout import HorizontalLayout, Layout, VerticalLayout
from fsui.qt.color import Color
from fsui.qt.drawingcontext import DrawingContext
from fsui.qt.qparent import QParent
from fsui.qt.qt import QPainter, Qt, QWidget
from fswidgets.overrides import overrides
from fswidgets.parentstack import ParentStack
from fswidgets.qt.core import Qt
from fswidgets.qt.widgets import QSplitter
from fswidgets.style import Style
from fswidgets.widget import Widget
from launcher.fswidgets2.style import Style


class Splitter(Widget):
    HORIZONTAL = "HORIZONTAL"
    VERTICAL = "VERTICAL"

    def __init__(
        self,
        orientation: Literal["HORIZONTAL", "VERTICAL"] = HORIZONTAL,
        *,
        parent: Optional[Widget] = None
    ):
        # __children Must be initialized early, because get_min_size can be
        # called via the super constructor.
        self.__children: List[Widget] = []
        parent = parent or ParentStack.top()
        super().__init__(
            parent,
            qwidget=QSplitter(
                Qt.Horizontal
                if orientation == self.HORIZONTAL
                else Qt.Vertical,
                QParent(parent),
            ),
        )
        # self.style = Style({}, style)
        self.style = Style({})
        self.layout = None

        self.qwidget.setHandleWidth(0)
        self.qwidget.setChildrenCollapsible(False)

        if parent.layout is not None:
            parent.layout.add(self, fill=True, expand=True)

        self.__fixedIndex = 0
        self.__horizontal = orientation == Splitter.HORIZONTAL

    # FIXME: Implement
    def get_min_height(self, width: int) -> int:
        minHeight = 0
        for child in self.__children:
            if self.__horizontal:
                minHeight = max(minHeight, child.get_min_height(width))
            else:
                minHeight += child.get_min_height(width)

        return minHeight

    # FIXME: Implement
    def get_min_width(self) -> int:
        # return super().get_min_width()
        # return 100
        minWidth = 0
        for child in self.__children:
            if self.__horizontal:
                minWidth += child.get_min_width()
            else:
                minWidth = max(minWidth, child.get_min_width())
        return minWidth

    def getSplitterPosition(self):
        sizes = self.qwidget.sizes()
        if self.__fixedIndex == 0:
            return sizes[0]
        else:
            return -sizes[1]

    @overrides
    def onChildAdded(self, widget: Widget):
        super().onChildAdded(widget)
        print("Splitter.onChildAdded", widget)
        self.__children.append(widget)
        # if len(self.__children) == 2:
        #     sizes: List[int] = []
        #     for child in self.__children:
        #         if self.__horizontal:
        #             sizes.append(child.get_min_width())
        #     print("setSizes", sizes)
        #     self.qwidget.setSizes(sizes)

    @overrides
    def onQWidgetChildAdded(self, qwidget: QWidget):
        print("Splitter.onQWidgetChildAdded", qwidget)

    def on_resize(self):
        super().on_resize()
        # FIXME: If the splitter is resized so that there is not room for the
        # minimum size of one of the widgets, move the splitter position to
        # account for this
        pass

    @property
    def qwidget(self) -> QSplitter:
        return cast(QSplitter, self.getQWidget())

    def setSplitterPosition(self, position: int, zeroableIndex: int = 0):
        if position > 0:
            self.qwidget.setStretchFactor(0, 0)
            self.qwidget.setStretchFactor(1, 1)
            self.qwidget.setSizes([position, 0])
            self.__fixedIndex = 1
        elif position < 0:
            self.qwidget.setStretchFactor(0, 1)
            self.qwidget.setStretchFactor(1, 0)
            self.qwidget.setSizes([0, -position])
            self.__fixedIndex = 0
        else:
            self.qwidget.setStretchFactor(zeroableIndex, 0)
            self.qwidget.setStretchFactor(not zeroableIndex, 1)
            self.qwidget.setSizes([0, 0])
            self.__fixedIndex = zeroableIndex

    def setStretchFactor(self, index: int, stretchFactor: int):
        self.qwidget.setStretchFactor(index, stretchFactor)
