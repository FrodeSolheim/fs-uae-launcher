from fscore.system import System
from fsgamesys.config.configevent import ConfigEvent
from fsgamesys.context import FSGameSystemContext
from fsgamesys.options.constants2 import (
    PARENT_H__,
    PARENT_W__,
    PARENT_X__,
    PARENT_Y__,
)
from fsui import Button, Icon
from fsui.context import get_window
from fswidgets.widget import Widget
from launcher.context import get_config, get_gscontext
from launcher.i18n import gettext
from system.classes.configdispatch import ConfigDispatch
from system.exceptionhandler import exceptionhandler


class StartButton(Button):
    MIN_WIDTH = 96

    def __init__(self, parent: Widget, dialog: bool = True) -> None:
        super().__init__(
            parent, gettext("Start"), icon=Icon("flag_green", "pkg:launcher")
        )
        ConfigDispatch(self, {"__running": self.__on_running_config})
        self.dialog = dialog
        self.set_min_width(self.MIN_WIDTH)

    @exceptionhandler
    def on_activate(self) -> None:
        StartButton.start(
            self, dialog=self.dialog, gscontext=get_gscontext(self)
        )

    @exceptionhandler
    def __on_running_config(self, event: ConfigEvent) -> None:
        isrunning = bool(event.value)
        self.set_enabled(not isrunning)

    @staticmethod
    def start(
        widget: Widget, dialog: bool = False, *, gscontext: FSGameSystemContext
    ) -> None:
        window = get_window(widget)
        if System.macos:
            position = window.getPosition()
            size = window.getSize()
        else:
            position = window.getUnscaledPosition()
            size = window.getUnscaledSize()
        config = get_config(widget)
        config.set(PARENT_X__, str(position[0]))
        config.set(PARENT_Y__, str(position[1]))
        config.set(PARENT_W__, str(size[0]))
        config.set(PARENT_H__, str(size[1]))

        # FIXME: Remove from LauncherApp
        from launcher.launcherapp import LauncherApp

        LauncherApp.start_game(dialog=dialog, gscontext=gscontext)
