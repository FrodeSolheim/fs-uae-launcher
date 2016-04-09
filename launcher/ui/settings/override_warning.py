import fsui
from launcher.i18n import gettext
from launcher.ui.behaviors.configbehavior import ConfigBehavior


class OverrideWarning(fsui.ImageView):

    def __init__(self, parent, name):
        fsui.ImageView.__init__(self, parent,fsui.Image(
            "launcher:res/16/warning_2.png"))
        setattr(self, "on_{0}_config".format(name), self.on_config)
        ConfigBehavior(self, [name])
        text = gettext(
            "Option {name} is overridden by current configuration".format(
                name=name))
        self.set_tool_tip(text)

    def on_config(self, value):
        self.show_or_hide(bool(value))
