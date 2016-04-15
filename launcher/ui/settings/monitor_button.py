import fsui
from fsbc.application import app
from launcher.i18n import gettext
from launcher.ui.behaviors.settingsbehavior import SettingsBehavior


class MonitorButton(fsui.ImageButton):
    def __init__(self, parent):
        self.left_icon = fsui.Image("launcher:res/16/monitor_left.png")
        self.middle_left_icon = fsui.Image(
            "launcher:res/16/monitor_middle_left.png")
        self.middle_right_icon = fsui.Image(
            "launcher:res/16/monitor_middle_right.png")
        self.right_icon = fsui.Image("launcher:res/16/monitor_right.png")
        super().__init__(parent, self.middle_left_icon)
        self.set_tooltip(gettext("Monitor to display FS-UAE on (left, "
                                 "middle-left, middle-right, right)"))
        self.set_min_width(40)
        self.monitor = ""
        SettingsBehavior(self, ["fullscreen", "monitor"])

    def on_fullscreen_setting(self, value):
        self.set_enabled(value == "1")

    def on_monitor_setting(self, value):
        if value == "left":
            self.monitor = "left"
            self.set_image(self.left_icon)
        elif value == "middle-right":
            self.monitor = "middle-right"
            self.set_image(self.middle_right_icon)
        elif value == "right":
            self.monitor = "right"
            self.set_image(self.right_icon)
        else:
            self.monitor = "middle-left"
            self.set_image(self.middle_left_icon)

    def on_activate(self):
        if self.monitor == "left":
            app.settings["monitor"] = ""
        elif self.monitor == "middle-left":
            app.settings["monitor"] = "middle-right"
        elif self.monitor == "middle-right":
            app.settings["monitor"] = "right"
        else:
            app.settings["monitor"] = "left"
