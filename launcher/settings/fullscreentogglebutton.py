from typing import List

from fsbc.application import app
from fsui import Image, ImageButton
from fswidgets.widget import Widget
from launcher.i18n import gettext
from launcher.launcher_settings import LauncherSettings


class FullscreenToggleButtonBase:
    """Mixin class also used by the workspace/titlebar fullscreen button."""

    def __init__(self, parent: Widget, icons: List[Image]) -> None:
        print("FullscreenToggle.__init__")
        super().__init__(parent, icons)
        self.icons = icons
        self.tooltip_text = gettext(
            "Toggle between windowed and full-screen mode"
        )
        self.fullscreen_mode = False
        self.on_setting("fullscreen", app.settings["fullscreen"], initial=True)
        LauncherSettings.add_listener(self)

    def on_activate(self):
        if self.fullscreen_mode:
            app.settings["fullscreen"] = "0"
        else:
            app.settings["fullscreen"] = "1"

    def onDestroy(self):
        LauncherSettings.remove_listener(self)
        super().onDestroy()

    def on_setting(self, key: str, value: str, initial: bool = False):
        print("on_setting", key, value, initial)
        if key == "fullscreen":
            if value == "1":
                self.fullscreen_mode = True
                self.__set_image(self.icons[1], initial=initial)
            else:
                self.fullscreen_mode = False
                self.__set_image(self.icons[0], initial=initial)

    def __set_image(self, image, initial):
        # if not initial:
        #     # pylint: disable=no-member
        self.set_image(image)


class ButtonWrapper(ImageButton):
    def __init__(self, parent: Widget, icons: List[Image]):
        super().__init__(parent, icons[0])


class FullscreenToggleButton(FullscreenToggleButtonBase, ButtonWrapper):
    def __init__(self, parent: Widget) -> None:
        super().__init__(
            parent,
            [
                Image("launcher:/data/windowed_16.png"),
                Image("launcher:/data/fullscreen_16.png"),
            ],
        )
        self.set_tooltip(self.tooltip_text)
        self.set_min_width(40)
