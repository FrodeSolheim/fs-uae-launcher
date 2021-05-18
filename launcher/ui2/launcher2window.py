from logging import getLogger
from typing import Optional

from fsgamesys.context import default_context
from fswidgets.decorators import constructor
from fswidgets.overrides import overrides
from fswidgets.widget import Widget
from launcher.components.UpdatesAvailablePanel import UpdatesAvailablePanel
from launcher.context import useSettings
from launcher.helpers.implicitconfighandler import ImplicitConfigHandler
from launcher.settings import get_launcher_window_title
from launcher.ui2.launcher2panel import Launcher2Panel
from launcher.ui2.mainmenu import MainMenu
from launcher.ui.imageloader import ImageLoader
from launcher.version import VERSION
from system.classes.window import Window
from system.classes.windowresizehandle import WindowResizeHandle
from system.exceptionhandler import withExceptionHandler
from system.special.logout import AsyncTaskRunner
from system.utilities.updater.checkforupdatestask import CheckForUpdatesTask

log = getLogger(__name__)


class Launcher2Window(Window):
    """Main window class."""

    @constructor
    def __init__(self, parent: Optional[Widget]):
        super().__init__(
            parent,
            title=f"{get_launcher_window_title()}  {VERSION}",
            menu=True,
        )

        settings = useSettings()

        # FIXME: Create new context instead - later
        self.gscontext = default_context()
        # FIXME: Access via context function useImageLoader?
        self.imageLoader = ImageLoader()
        self.implicitConfigHandler = ImplicitConfigHandler(self)

        # self.layout.add(Launcher2Panel(), expand=True, fill=True)
        self.panel = Launcher2Panel()
        WindowResizeHandle()

        initialSize = self.getDefaultSize()
        log.debug(f"Setting initial window size to {initialSize}")
        self.setSize(initialSize)

        windowState = settings.getLauncherWindowState()
        if windowState:
            # self.setWindowState(windowState)
            minWidth = self.get_min_width()
            if windowState.width < minWidth:
                windowState.width = minWidth
            minHeight = self.get_min_height(windowState.width)
            if windowState.height < minHeight:
                windowState.height = minHeight
            # if windowState.width and windowState.height:
            # FIXME: Ideally also check position and size against available
            # screen estate
            # self.setPositionAndSize(
            #     (windowState.x, windowState.y),
            #     (windowState.width, windowState.height),
            # )

            # FIXME: Maybe client size should be default / same as size
            # self.setClientPosition((windowState.x, windowState.y))
            # self.setClientSize((windowState.width, windowState.height))
            self.setPositionAndSize(
                (windowState.x, windowState.y),
                (windowState.width, windowState.height),
            )
            # self.setPosition((windowState.x, windowState.y))
            # self.setSize((windowState.width, windowState.height))

            if windowState.maximized:
                self.maximize()

        split = settings.getLauncherBottomSplit()
        if split is not None:
            self.panel.right.setSplitterPosition(-split)
        split = settings.getLauncherMainSplit()
        if split is not None:
            self.panel.setSplitterPosition(split)

        if settings.checkForUpdates:
            self.checkForUpdates()

    def getDefaultSize(self):
        return (1280, 720)

    @overrides
    def onClose(self):
        super().onClose()

        # FIXME: Maybe client size should be default / same as size
        print("--------------")
        print(
            "Position", self.getPosition(), "window", self.getWindowPosition()
        )
        print("Size", self.getSize(), "window", self.getWindowSize())
        print(self.isMaximized())
        print(self.getWindowState())
        print("--------------")

        # FIXME: Ideally, we want to save the window position and size we had
        # *before* maximizing the window, so that we can restore that state in
        # addition to maximize it.
        # FIXME: We also want to differentiate between client size and size incl
        # window decorations

        # getSize vs getWindowSize
        # getPosition vs getWindowPosition
        # getClientSize
        # getClientPosition

        settings = useSettings()
        settings.setLauncherWindowState(self.getWindowState())
        settings.setLauncherMainSplit(self.panel.getSplitterPosition())
        settings.setLauncherBottomSplit(-self.panel.right.getSplitterPosition())

    @overrides
    def onDestroy(self):
        super().onDestroy()
        self.imageLoader.stop()

    @withExceptionHandler
    def onMenu(self):
        return MainMenu(self)

    # FIXME: Maybe rename to restorePreferredSize and put in TopLevelWidget
    # + getPreferredSize (new funcion) in Widget (for overriding) and/or maybe
    # a corresponding setPreferredSize
    def restoreDefaultSize(self):
        self.setMaximized(False)
        self.setSize(self.getDefaultSize())
        self.panel.restoreDefaultSplitterPosition()
        self.panel.right.restoreDefaultSplitterPosition()

    def checkForUpdates(self):
        def onResult(result):
            if len(CheckForUpdatesTask.findUpdates(result)) > 0:
                print("Updates are available!")
                UpdatesAvailablePanel(self).show()

        task = CheckForUpdatesTask()
        self.addDestroyListener(AsyncTaskRunner(onResult).run(task).cancel)

    # FIXME: Move to widget
    def addDestroyListener(self, listener):
        self.destroyed.connect(listener)
