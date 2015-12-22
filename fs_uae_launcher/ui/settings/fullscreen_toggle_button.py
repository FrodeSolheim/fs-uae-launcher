from fsbc.Application import app
import fsui as fsui
from ...I18N import gettext
from ...Settings import Settings


class FullscreenToggleButton(fsui.ImageButton):

    def __init__(self, parent):
        self.windowed_icon = fsui.Image(
            "fs_uae_launcher:res/windowed_16.png")
        self.fullscreen_icon = fsui.Image(
            "fs_uae_launcher:res/fullscreen_16.png")
        fsui.ImageButton.__init__(self, parent, self.windowed_icon)
        self.set_tooltip(
            gettext("Toggle Between Windowed and Full-Screen Mode"))
        self.set_min_width(40)
        self.fullscreen_mode = False
        self.on_setting("fullscreen", app.settings["fullscreen"])
        Settings.add_listener(self)

    def on_destroy(self):
        Settings.remove_listener(self)

    def on_setting(self, key, value):
        if key == "fullscreen":
            if value == "1":
                self.fullscreen_mode = True
                self.set_image(self.fullscreen_icon)
            else:
                self.fullscreen_mode = False
                self.set_image(self.windowed_icon)

    def on_activate(self):
        if self.fullscreen_mode:
            app.settings["fullscreen"] = "0"
        else:
            app.settings["fullscreen"] = "1"
