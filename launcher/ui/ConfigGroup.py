import fsui as fsui
from ..launcher_config import LauncherConfig
from ..i18n import gettext
from ..launcher_settings import LauncherSettings
from launcher.ui.newbutton import NewButton
from launcher.ui.savebutton import SaveButton


class ConfigGroup(fsui.Group):

    def __init__(self, parent, new_button=True):
        fsui.Group.__init__(self, parent)
        self.layout = fsui.VerticalLayout()

        # heading_label = fsui.HeadingLabel(self, _("Configuration"))
        # self.layout.add(heading_label, margin=10)
        # self.layout.add_spacer(0)

        hori_layout = fsui.HorizontalLayout()
        self.layout.add(hori_layout, fill=True)

        # dummy label for sizing purposes
        # label = fsui.HeadingLabel(self, "")
        # hori_layout.add(label, margin_top=10, margin_bottom=10)

        if new_button:
            label_stand_in = fsui.Panel(self)
            tw, th = label_stand_in.measure_text(gettext("Configuration"))
            label_stand_in.set_min_height(th)
            hori_layout.add(label_stand_in, margin_top=10, margin_bottom=10)

            hori_layout.add(NewButton(self), margin_left=10, margin_right=10)

        # self.open_button = IconButton(self, "open_button.png")
        # self.open_button.set_tooltip(_("Open Configuration"))
        # self.open_button.disable()
        # self.open_button.activated.connect(self.on_open_button)
        # hori_layout.add(self.open_button, margin=10)

        self.config_name_field = fsui.TextField(self)
        hori_layout.add(self.config_name_field, expand=True, margin=10,
                        margin_top=0, margin_bottom=0)

        hori_layout.add(SaveButton(self), margin_left=10, margin_right=10)

        # self.save_button = IconButton(self, "save_button.png")
        # # self.save_button.disable()
        # self.save_button.set_tooltip(gettext("Save Configuration"))
        # self.save_button.activated.connect(self.on_save_button)
        # hori_layout.add(self.save_button, margin=10,
        #                 margin_top=0, margin_bottom=0)

        self.on_setting("config_name", LauncherSettings.get("config_name"))
        self.config_name_field.on_changed = self.on_config_name_changed

        # Config.add_listener(self)
        LauncherSettings.add_listener(self)

        # self.on_setting("config_changed", Settings.get("config_changed"))
        # self.on_config("__changed", Config.get("__changed"))

    def on_destroy(self):
        # Config.remove_listener(self)
        LauncherSettings.remove_listener(self)

    # def on_config(self, key, value):
    #     if key == "__changed":
    #         self.save_button.enable(value == "1")

    def on_setting(self, key, value):
        # if key == "config_changed":
        #     self.save_button.enable(value == "1")
        if key == "config_name":
            if value != self.config_name_field.get_text().strip():
                self.config_name_field.set_text(value)

    def on_config_name_changed(self):
        text = self.config_name_field.get_text().strip()
        LauncherSettings.set("config_name", text)
        # Settings.set("config_changed", "1")
        LauncherConfig.set("__changed", "1")
        # FIXME: remove
        # Config.set("title", text)

    @staticmethod
    def new_config():
        NewButton.new_config()
