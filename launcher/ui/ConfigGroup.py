import fsui
from launcher.i18n import gettext
from launcher.launcher_config import LauncherConfig
from launcher.launcher_settings import LauncherSettings
from launcher.ui.behaviors.settingsbehavior import SettingsBehavior
from launcher.ui.newbutton import NewButton
from launcher.ui.savebutton import SaveButton


class ConfigGroup(fsui.Group):
    def __init__(self, parent, new_button=True):
        fsui.Group.__init__(self, parent)
        self.layout = fsui.VerticalLayout()
        hori_layout = fsui.HorizontalLayout()
        self.layout.add(hori_layout, fill=True)
        if new_button:
            label_stand_in = fsui.Panel(self)
            tw, th = label_stand_in.measure_text(gettext("Configuration"))
            label_stand_in.set_min_height(th)
            hori_layout.add(label_stand_in, margin_top=10, margin_bottom=10)

            hori_layout.add(NewButton(self), margin_left=10, margin_right=10)
        self.config_name_field = fsui.TextField(self)
        hori_layout.add(self.config_name_field, expand=True, margin=10,
                        margin_top=0, margin_bottom=0)
        hori_layout.add(SaveButton(self), margin_left=10, margin_right=10)
        self.config_name_field.on_changed = self.on_config_name_changed
        SettingsBehavior(self, ["config_name"])

    def on_config_name_setting(self, value):
        if value != self.config_name_field.get_text().strip():
            with self.config_name_field.changed.inhibit:
                self.config_name_field.set_text(value)

    def on_config_name_changed(self):
        text = self.config_name_field.get_text().strip()
        LauncherSettings.set("config_name", text)
        LauncherConfig.set("__changed", "1")

    @staticmethod
    def new_config():
        NewButton.new_config()
