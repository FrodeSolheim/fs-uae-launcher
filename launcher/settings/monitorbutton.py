from fsbc.application import app
from fsui import Image, ImageButton
from launcher.i18n import gettext
from launcher.launcher_settings import LauncherSettings


class MonitorButtonBase:
    def __init__(self, parent, icons):
        super().__init__(parent, icons)
        self.icons = icons
        self.monitor = ""
        self.tooltip_text = gettext(
            "Monitor to display the emulator on (left, "
            "middle-left, middle-right, right)"
        )

        # self.on_setting("fullscreen", app.settings["fullscreen"], initial=True)
        self.on_setting("monitor", app.settings["monitor"], initial=True)
        LauncherSettings.add_listener(self)

    def on_activate(self):
        if self.monitor == "left":
            app.settings["monitor"] = ""
        elif self.monitor == "middle-left":
            app.settings["monitor"] = "middle-right"
        elif self.monitor == "middle-right":
            app.settings["monitor"] = "right"
        else:
            app.settings["monitor"] = "left"

    def on_destroy(self):
        LauncherSettings.remove_listener(self)
        super().on_destroy()

    def on_setting(self, key, value, initial=False):
        if key == "fullscreen":
            # self.set_enabled(value == "1")
            pass
        elif key == "monitor":
            if value == "left":
                self.monitor = "left"
                self.__set_image(self.icons[0])
            elif value == "middle-right":
                self.monitor = "middle-right"
                self.__set_image(self.icons[2])
            elif value == "right":
                self.monitor = "right"
                self.__set_image(self.icons[3])
            else:
                self.monitor = "middle-left"
                self.__set_image(self.icons[1])

    def __set_image(self, image, initial=False):
        self.image = image
        if not initial:
            # pylint: disable=no-member
            self.set_image(image)


class ButtonWrapper(ImageButton):
    def __init__(self, parent, icons):
        super().__init__(parent, icons[0])


class MonitorButton(MonitorButtonBase, ButtonWrapper):
    def __init__(self, parent):
        super().__init__(
            parent,
            [
                Image("launcher:/data/16x16/monitor_left.png"),
                Image("launcher:/data/16x16/monitor_middle_left.png"),
                Image("launcher:/data/16x16/monitor_middle_right.png"),
                Image("launcher:/data/16x16/monitor_right.png"),
            ],
        )
        self.set_tooltip(self.tooltip_text)
        self.set_min_width(40)
