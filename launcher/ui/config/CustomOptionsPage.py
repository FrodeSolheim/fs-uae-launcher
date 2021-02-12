import fsui
from fsgamesys.context import fsgs
from launcher.i18n import gettext
from launcher.launcher_config import LauncherConfig


class CustomOptionsPage(fsui.Panel):
    def __init__(self, parent):
        fsui.Panel.__init__(self, parent)
        self.layout = fsui.VerticalLayout()

        label = fsui.MultiLineLabel(
            self,
            gettext(
                "You can write key = value pairs here to set FS-UAE options "
                "not currently supported by the user interface. This is only a "
                "temporary feature until the GUI supports all options "
                "directly."
            ),
            760,
        )
        self.layout.add(label, fill=True, margin_bottom=10)
        label = fsui.MultiLineLabel(
            self,
            gettext(
                "The options specified here will apply to this configuration "
                "only."
            ),
            760,
        )
        self.layout.add(label, fill=True, margin_bottom=10)

        hor_layout = fsui.HorizontalLayout()
        self.layout.add(hor_layout, fill=True, expand=True)

        # hor_layout.add_spacer(20)
        self.text_area = fsui.TextArea(self, font_family="monospace")
        self.text_area.set_min_width(760)
        self.text_area.set_min_height(400)
        self.text_area.set_text(initial_text())
        hor_layout.add(self.text_area, fill=True, expand=True)
        # hor_layout.add_spacer(20)

        # self.layout.add_spacer(20)

        self.get_window().add_close_listener(self.on_close_window)

    def on_close_window(self):
        self.update_config()

    def on_close_button(self):
        self.end_modal(0)

    def update_config(self):
        text = self.text_area.get_text()
        update_config = {}
        # First mark all unknown config values as cleared
        for key in list(fsgs.config.values.keys()):
            if key not in LauncherConfig.default_config:
                update_config[key] = ""
        # Then we overwrite with specific values
        for line in text.split("\n"):
            line = line.strip()
            parts = line.split("=", 1)
            if len(parts) == 2:
                key = parts[0].strip()
                # if key in Config.no_custom_config:
                #     continue
                value = parts[1].strip()
                update_config[key] = value
        # Finally, set everything at once
        LauncherConfig.set_multiple(update_config.items())


def initial_text():
    text = []
    keys = fsgs.config.values.keys()
    for key in sorted(keys):
        # FIXME: Move to LauncherConfig as a method, maybe use
        # is_custom_option.
        if key in LauncherConfig.no_custom_config:
            continue
        if key.startswith("__implicit_"):
            continue

        value = fsgs.config.values[key]
        if not value:
            continue
        text.append("{0} = {1}\n".format(key, value))
    return "".join(text)
