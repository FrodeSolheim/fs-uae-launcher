from typing import Optional

import fsui
from fscore.system import System
from fsui.qt.panel import Panel
from fswidgets.types import Size
from fswidgets.widget import Widget
from launcher.context import get_launcher_theme
from system.classes.windowborder import WindowBorder

from .titlebar import TitleBar


class Window(fsui.Window):
    def __init__(
        self,
        parent: Optional[Widget],
        *,
        title: str = "",
        size: Optional[Size] = None,
        menu: bool = False,
        maximizable: bool = True,
        minimizable: bool = True,
        escape: bool = False
    ):
        self.theme = get_launcher_theme(self)
        window_parent = None
        # window_parent = parent
        border = self.theme.titlebar_system()
        super().__init__(
            window_parent,
            title,
            border=border,
            maximizable=maximizable,
            minimizable=minimizable,
            escape=escape,
        )
        if size is not None:
            self.setSize(size)
        self.layout = fsui.VerticalLayout()

        useBorder = True
        if System.macos:
            # macOS already puts a thin border around the windows, so we do not
            # want to double it.
            useBorder = False
        self.windowBorderAroundTitle = True

        if useBorder:
            borderWidth = 1
            self.windowNormalBorders.top = borderWidth
            self.windowNormalBorders.right = borderWidth
            self.windowNormalBorders.bottom = borderWidth
            self.windowNormalBorders.left = borderWidth
            self.windowBorderWidget = WindowBorder(self)
        else:
            self.windowBorderWidget = None

        # self.set_background_color(self.theme.window_bgcolor())
        if not self.theme.titlebar_system():
            self.__titlebar = TitleBar(
                self,
                title=title,
                menu=menu,
                minimizable=minimizable,
                maximizable=maximizable,
            )
            # self.layout.add(self.__titlebar, fill=True)
            if self.windowBorderAroundTitle:
                self.windowMargins.top = 40
            else:
                # FIXME: Don't like this, when maximized we probably want to
                # disable borders and this will cut into the titlebar margin
                # Better to use max() for margins instead + ?
                self.windowMargins.top = 40 - self.windowBorders.top
        else:
            self.__titlebar = None

        # self.qcontainer = QWidget()
        # self.qcontainer.setParent(self.qwidget)

        self.container = Panel(self)
        self.container.setBackgroundColor(self.theme.window_bgcolor())
        # self.container.setParent(self.qwidget)

    # def getPosition(self) -> Point:
    #     position = super().getPosition()
    #     # FIXME: ...hardcoded
    #     return (position[0], position[1] + 40)

    # def getSize(self) -> Size:
    #     size = super().getSize()
    #     # FIXME: ...hardcoded
    #     return (size[0], size[1] - 40)

    # def setPosition(self, position: Point):
    #     # FIXME: ...hardcoded
    #     super().setPosition((position[0], position[1] - 40))

    # def setSize(self, size: Size):
    #     # FIXME: ...hardcoded
    #     super().setSize((size[0], size[1] + 40))

    def on_resize(self):
        super().on_resize()
        print(
            "Window.resize, maximized =",
            self.isMaximized(),
            "windowBorders",
            self.windowBorders,
        )
        if self.windowBorderWidget:
            w, h = self.getRealSize()
            self.windowBorderWidget.setPositionAndSize((0, 0), (w, h))
        if self.__titlebar:
            w, h = self.getRealSize()
            # self.__titlebar.setPosition((0, 0))
            # self.__titlebar.setSize((w, self.__titlebar.getSize()[1]))
            if self.windowBorderAroundTitle:
                self.__titlebar.setPositionAndSize(
                    (self.windowBorders.left, self.windowBorders.top),
                    (
                        w - self.windowBorders.left - self.windowBorders.right,
                        40,
                    ),
                )
            else:
                self.__titlebar.setPositionAndSize(
                    (0, 0),
                    (w, 40),
                )

        x = self.windowBorders.left + self.windowMargins.left
        y = self.windowBorders.top + self.windowMargins.top
        width, height = self.getSize()
        # Margins are already account for in getSize
        # width -= self.windowMargins.left + self.windowMargins.right
        # height -= self.windowMargins.top + self.windowMargins.bottom
        print(x, y, width, height)
        # self.qcontainer.setGeometry(x, y, width, height)
        self.container.setPositionAndSize((x, y), (width, height))

    # -------------------------------------------------------------------------
    # Temporary solution until size/positions and offsets for custom
    # decoration windows are sorted out.

    # def getClientPosition(self) -> Point:
    #     position = self.getPosition()
    #     # FIXME: ...hardcoded
    #     return (position[0], position[1] + 40)

    # def getClientSize(self) -> Size:
    #     size = self.getSize()
    #     # FIXME: ...hardcoded
    #     return (size[0], size[1] - 40)

    # def setClientPosition(self, position: Point):
    #     # FIXME: ...hardcoded
    #     self.setPosition((position[0], position[1] - 40))

    # def setClientSize(self, size: Size):
    #     # FIXME: ...hardcoded
    #     self.setSize((size[0], size[1] + 40))
