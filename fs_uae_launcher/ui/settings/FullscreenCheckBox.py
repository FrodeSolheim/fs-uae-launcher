import fsui as fsui
from ...Settings import Settings
from ...I18N import gettext


class FullscreenCheckBox(fsui.CheckBox):

    def __init__(self, parent):
        fsui.CheckBox.__init__(self, parent, gettext("Fullscreen"))
        self.on_setting("fullscreen", Settings.get("fullscreen"))
        Settings.add_listener(self)

    def on_destroy(self):
        Settings.remove_listener(self)

    def on_setting(self, key, value):
        if key == "fullscreen":
            self.check(value == "1")

    def on_change(self):
        if self.is_checked():
            Settings.set("fullscreen", "1")
        else:
            Settings.set("fullscreen", "0")
