import fsui
from launcher.context import get_config
from launcher.ui.behaviors.platformbehavior import AmigaEnableBehavior

from ..HelpButton import HelpButton


class WHDLoadGroup(fsui.Panel):
    def __init__(self, parent):
        fsui.Panel.__init__(self, parent)
        AmigaEnableBehavior(self)
        self.layout = fsui.VerticalLayout()
        self.text_field = fsui.TextField(self, "")
        hori_layout = fsui.HorizontalLayout()
        self.layout.add(hori_layout, fill=True, margin=10)
        hori_layout.add(self.text_field, expand=True)
        self.help_button = HelpButton(
            self, "https://fs-uae.net/whdload-support"
        )
        hori_layout.add(self.help_button, margin_left=10)
        self.initialize_from_config()
        self.set_config_handlers()

    def initialize_from_config(self):
        self.on_config(
            "x_whdload_args", get_config(self).get("x_whdload_args")
        )

    def set_config_handlers(self):
        self.text_field.on_changed = self.on_text_changed
        get_config(self).add_listener(self)

    def onDestroy(self):
        get_config(self).remove_listener(self)
        super().onDestroy()

    def on_config(self, key, value):
        if key == "x_whdload_args":
            if value != self.text_field.text():
                self.text_field.set_text(value)

    def on_text_changed(self):
        get_config(self).set("x_whdload_args", self.text_field.text())
