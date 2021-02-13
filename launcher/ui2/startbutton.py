from fsgamesys.options.constants2 import (
    PARENT_H__,
    PARENT_W__,
    PARENT_X__,
    PARENT_Y__,
)
from fsui import Button, Icon
from fsui.context import get_window
from launcher.context import get_config, get_gscontext
from launcher.i18n import gettext
from launcher.system.classes.configdispatch import ConfigDispatch
from launcher.system.exceptionhandler import exceptionhandler


class StartButton(Button):
    MIN_WIDTH = 96

    def __init__(self, parent, dialog=True):
        super().__init__(
            parent, gettext("Start"), icon=Icon("flag_green", "pkg:launcher")
        )
        ConfigDispatch(self, {"__running": self.__on_running_config})
        self.dialog = dialog
        self.set_min_width(self.MIN_WIDTH)

    @exceptionhandler
    def on_activate(self):
        StartButton.start(
            self, dialog=self.dialog, gscontext=get_gscontext(self)
        )

    @exceptionhandler
    def __on_running_config(self, event):
        isrunning = bool(event.value)
        self.set_enabled(not isrunning)

    @staticmethod
    def start(widget, dialog=False, *, gscontext):
        window = get_window(widget)
        pos = window.unscaled_position()
        size = window.unscaled_size()
        config = get_config(widget)
        config.set(PARENT_X__, str(pos[0]))
        config.set(PARENT_Y__, str(pos[1]))
        config.set(PARENT_W__, str(size[0]))
        config.set(PARENT_H__, str(size[1]))

        # FIXME: Remove from LauncherApp
        from launcher.launcherapp import LauncherApp

        LauncherApp.start_game(dialog=dialog, gscontext=gscontext)
