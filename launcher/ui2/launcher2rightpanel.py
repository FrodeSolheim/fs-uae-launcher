from fsgamesys.config.configevent import ConfigEvent
from fsui import Color, HorizontalLayout, Panel, VerticalLayout
from fswidgets.splitter import Splitter
from fswidgets.widget import Widget
from launcher.ui2.configpanel import ConfigPanel
from launcher.ui2.launcher2bottompanel import Launcher2BottomPanel
from launcher.ui2.launcher2colors import Launcher2Colors
from launcher.ui2.launcher2sidepanel import Launcher2SidePanel
from launcher.ui2.launcher2toppanel import Launcher2TopPanel
from system.classes.configdispatch import ConfigDispatch


class Launcher2MainPanel(Panel):
    def __init__(self, parent: Widget) -> None:
        super().__init__(parent=parent)

        horilayout = HorizontalLayout()
        self.layout.add(horilayout, fill=True, expand=True)

        vertlayout = VerticalLayout()
        horilayout.add(vertlayout, fill=True, expand=True)

        self.top_panel = Launcher2TopPanel(self)
        vertlayout.add(self.top_panel, fill=True)

        self.configpanel = ConfigPanel(self)
        # FIXME: Refer to theme? dialog_bg_color?
        self.configpanel.setBackgroundColor(
            Color(Launcher2Colors.CONFIG_PANEL_COLOR)
        )
        # self.configpanel.set_background_color(Color(0xBBBBBB))
        vertlayout.add(self.configpanel, fill=True, expand=True)

        # self.bottom_panel = Launcher2BottomPanel(self)
        # self.layout.add(self.bottom_panel, fill=True)

        design_test = True
        if design_test:
            self.side = Launcher2SidePanel(self)
            horilayout.add(self.side, fill=True)

            # The Launcher should fit into a 1280x720 display, with
            # common/reasonable GUI elements such as a task bar.
            # Or maybe use 1366x768
            # Or maybe 1280x768 to support 1280x1024 and 1366x768.
            # Windows 10 taskbar width/side: 62 pixels
            # Windows 10 taskbar height/bottom: 40 pixels
            # screen_size = (1280, 720)
            # screen_size = (1366, 768)

            # min_width = screen_size[0] - 62
            # Subtracting an additional 40 For Launcher title bar
            # min_height = screen_size[1] - 40 - 40

            # self.getParent().set_min_size((min_width, min_height))
            # self.getParent().left.set_min_width(380)

            # self.getParent().getParent().set_min_size((1280, 720 - 40))

            # For now, make the minimum _client size_ 1280x720 which will cause
            # the window with decorations to be 1280x740. This should not be
            # the min. required size going forward though. Too big for
            # 768-height screens with bottom Windows 10 taskbar...
            # self.parent().set_min_size((1280, 720))


class Launcher2RightPanel(Splitter):
    def __init__(self, parent: Widget) -> None:
        super().__init__(Splitter.VERTICAL, parent=parent)

        self.top_panel = Launcher2MainPanel(self)

        # This is used by code in other modules
        # self.configpanel = self.top_panel.configpanel

        # vertlayout.add(self.top_panel, fill=True)

        self.bottom_panel = Launcher2BottomPanel(self)

        # self.setSplitterPosition(-self.bottom_panel.get_min_height(0))
        self.setSplitterPosition(self.getDefaultSplitterPosition())

        ConfigDispatch(self, {"__running": self.__on_running_config})

    def getDefaultSplitterPosition(self) -> int:
        return -self.bottom_panel.getPreferredInitialHeight()

    def __on_running_config(self, event: ConfigEvent) -> None:
        isrunning = bool(event.value)
        # if self.running_panel.visible() != isrunning:
        #     # self.running_panel.set_visible(isrunning)
        #     # self.top_panel.set_visible(not isrunning)
        #     # self.top_panel.set_enabled(not isrunning)

        # self.configpanel.book.set_enabled(not isrunning)
        # self.top_panel.set_enabled(not isrunning)
        self.top_panel.configpanel.book.set_enabled(not isrunning)
        self.top_panel.top_panel.set_enabled(not isrunning)

        self.top_panel.layout.update()

    def restoreDefaultSplitterPosition(self) -> None:
        self.setSplitterPosition(self.getDefaultSplitterPosition())
