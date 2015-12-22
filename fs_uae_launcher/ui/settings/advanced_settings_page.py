import fsui
from fs_uae_launcher.Config import Config
from fs_uae_launcher.I18N import gettext
from fs_uae_launcher.Settings import Settings
from fs_uae_launcher.ui.settings.settings_page import SettingsPage
from fsbc.Application import app


class AdvancedSettingsPage(SettingsPage):
    def __init__(self, parent):
        super().__init__(parent)
        icon = fsui.Icon("settings", "pkg:fs_uae_workspace")
        gettext("Advanced")
        title = gettext("Advanced Settings")
        subtitle = gettext("Specify global options and settings which does "
                           "not have UI controls")
        self.add_header(icon, title, subtitle)

        label = fsui.MultiLineLabel(self, (
            "You can write key = value pairs here to set FS-UAE options "
            "not currently supported by the user interface. This is only a "
            "temporary feature until the GUI supports all options "
            "directly. "), 640)
        self.layout.add(label, fill=True, margin_bottom=10)

        label = fsui.MultiLineLabel(self, (
            "The options specified here are global and will apply to all "
            "configurations. Config options such as hardware and memory "
            "options will be ignored. Options suitable here are options "
            "like theme options."), 640)
        self.layout.add(label, fill=True, margin_bottom=10)

        self.text_area = fsui.TextArea(self, font_family="monospace")
        self.text_area.set_text(self.get_initial_text())
        self.layout.add(self.text_area, fill=True, expand=True)
        self.text_area.changed.connect(self.update_settings)

    def update_settings(self):
        text = self.text_area.get_text()
        # FIXME: accessing values directly here, not very nice
        keys = list(app.settings.values.keys())
        for key in keys:
            if key not in Settings.default_settings:
                Settings.set(key, "")
                del app.settings.values[key]

        for line in text.split("\n"):
            line = line.strip()
            if line.startswith("# You can write key = value pairs here"):
                continue
            parts = line.split("=", 1)
            if len(parts) == 2:
                key = parts[0].strip()
                # if key in Settings.default_settings:
                #     continue
                value = parts[1].strip()
                app.settings[key] = value

    def get_initial_text(self):
        text = ""
        # FIXME: accessing values directly here, not very nice
        keys = app.settings.values.keys()
        for key in sorted(keys):
            if key in Settings.default_settings:
                continue
            # #print("(settings) ignoring key", key)
            #    text += "# key {0} will be ignored\n".format(key)
            # if key in Config.config_keys:
            #     print("(settings) ignoring key", key)
            #     continue
            if key in Config.config_keys:
                # print("(settings) ignoring key", key)
                text += "\n# {0} is ignored here " \
                        "(use config dialog instead)\n".format(key)
            value = app.settings[key]
            if Config.get(key):
                text += "\n# {0} is overridden by current " \
                        "configuration\n".format(key)
            text += "{0} = {1}\n".format(key, value)
            if Config.get(key):
                text += "\n"
            if key in Config.config_keys:
                text += "\n"
        return text
