from launcher.context import get_config
from launcher.ui.statusbar.StatusElement import StatusElement


class LanguageElement(StatusElement):
    def __init__(self, parent, language, icon, tool_tip=""):
        StatusElement.__init__(self, parent)
        self.set_min_width(32)
        self.icon = icon
        self.language = language
        self.languages = ""
        self.hide()
        if tool_tip:
            self.set_tooltip(tool_tip)

        config = get_config(self)
        config.add_listener(self)
        self.on_config("languages", config.get("languages"))

    def onDestroy(self):
        config = get_config(self)
        config.remove_listener(self)
        super().onDestroy()

    def on_config(self, key, value):
        if key == "languages":
            if value != self.languages:
                self.languages = value
                if self.language in value:
                    self.show()
                else:
                    self.hide()
