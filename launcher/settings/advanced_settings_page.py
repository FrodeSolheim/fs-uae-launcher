import fsui
from fsbc.application import app
from launcher.i18n import gettext
from launcher.launcher_config import LauncherConfig
from launcher.launcher_settings import LauncherSettings
from launcher.settings.settings_page import SettingsPage


class AdvancedSettingsPage(SettingsPage):
    def __init__(self, parent):
        super().__init__(parent)
        # icon = fsui.Icon("settings", "pkg:workspace")
        # title = gettext("Advanced")
        # subtitle = gettext(
        #     "Specify global options and settings which does "
        #     "not have UI controls"
        # )
        # self.add_header(icon, title, subtitle)

        label = fsui.MultiLineLabel(
            self,
            gettext(
                "You can write key = value pairs here to set FS-UAE options "
                "not currently supported by the user interface. This is only a "
                "temporary feature until the GUI supports all options "
                "directly."
            ),
            640,
        )
        self.layout.add(label, fill=True, margin_bottom=10)

        label = fsui.MultiLineLabel(
            self,
            gettext(
                "The options specified here are global and will apply to all "
                "configurations. Config options such as hardware and memory "
                "options will be ignored. Options suitable here are options "
                "like theme options."
            ),
            640,
        )
        self.layout.add(label, fill=True, margin_bottom=10)

        self.text_area = fsui.TextArea(self, font_family="monospace")
        self.text_area.set_text(self.get_initial_text())
        self.layout.add(self.text_area, fill=True, expand=True)
        self.text_area.changed.connect(self.update_settings)

        self.set_min_height(600)

    def update_settings(self):
        text = self.text_area.get_text()
        # FIXME: accessing values directly here, not very nice
        keys = list(app.settings.values.keys())
        for key in keys:
            if key not in LauncherSettings.default_settings:
                LauncherSettings.set(key, "")
                del app.settings.values[key]

        for line in text.split("\n"):
            line = line.strip()
            parts = line.split("=", 1)
            if len(parts) == 2:
                key = parts[0].strip()
                # if key in Settings.default_settings:
                #     continue
                value = parts[1].strip()
                app.settings[key] = value

    @staticmethod
    def get_initial_text():
        text = ""
        # FIXME: accessing values directly here, not very nice
        keys = app.settings.values.keys()
        for key in sorted(keys):
            if key in LauncherSettings.default_settings:
                continue
            # if key in LauncherConfig.config_keys:
            #     # print("(settings) ignoring key", key)
            #     text += "\n# {0} is ignored here " \
            #             "(use config dialog instead)\n".format(key)
            if LauncherConfig.is_config_only_option(key):
                text += (
                    "\n# {0} will here function as a global config "
                    "default and may cause\nunexpected problems. It is "
                    "recommended to only use this as a per-config "
                    "option.\n".format(key)
                )
            value = app.settings[key]
            # if LauncherConfig.get(key):
            #     text += (
            #         "\n# {0} is overridden by current "
            #         "configuration\n".format(key)
            #     )
            text += "{0} = {1}\n".format(key, value)
            # if LauncherConfig.get(key):
            #     text += "\n"
            if key in LauncherConfig.config_keys:
                text += "\n"
        return text
