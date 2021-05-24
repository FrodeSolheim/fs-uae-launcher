from typing import Optional

from fsui import HorizontalLayout
from fswidgets.panel import Panel
from fswidgets.parentstack import ParentStack
from fswidgets.splitter import Splitter
from fswidgets.widget import Widget
from launcher.ui2.launcher2leftpanel import Launcher2LeftPanel
from launcher.ui2.launcher2rightpanel import Launcher2RightPanel


# class Launcher2Panel(Panel):
class Launcher2Panel(Splitter):
    def __init__(self, parent: Optional[Widget] = None):
        super().__init__(parent=parent)
        # horilayout = HorizontalLayout()
        # self.layout.add(horilayout, fill=True, expand=True)

        self.left = Launcher2LeftPanel(self)
        # self.left.set_min_width(380)
        self.left.set_min_width(240)

        # - 40 for titlebar, - 40 for windows taskbar
        self.set_min_size((1100, 768 - 40 - 40))

        # horilayout.add(self.left, fill=True)
        self.right = Launcher2RightPanel(self)
        # horilayout.add(self.right, fill=True, expand=True)

        # self.setStretchFactor(0, 0)
        # self.setStretchFactor(1, 1)
        # self.setWidgetSize(0, 380)
        self.setSplitterPosition(self.getDefaultSplitterPosition())

        # design_test = True
        # if design_test:
        #     self.side = Panel(self)
        #     self.side.set_background_color(Color(0xCCCCCC))
        #     self.side.set_min_width(320)
        #     horilayout.add(self.side, fill=True)

        #     # The Launcher should fit into a 1280x720 display, with
        #     # common/reasonable GUI elements such as a task bar.
        #     # Or maybe use 1366x768
        #     # Or maybe 1280x768 to support 1280x1024 and 1366x768.
        #     # Windows 10 taskbar width/side: 62 pixels
        #     # Windows 10 taskbar height/bottom: 40 pixels
        #     # screen_size = (1280, 720)
        #     screen_size = (1366, 768)

        #     min_width = screen_size[0] - 62
        #     # Subtracting an additional 40 For Launcher title bar
        #     min_height = screen_size[1] - 40 - 40

        #     self.set_min_size((min_width, min_height))
        #     self.left.set_min_width(360)

    def getDefaultSplitterPosition(self):
        return 380

    def restoreDefaultSplitterPosition(self):
        self.setSplitterPosition(self.getDefaultSplitterPosition())
