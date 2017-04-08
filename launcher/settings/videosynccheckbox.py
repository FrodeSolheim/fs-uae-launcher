import fsui
from launcher.i18n import gettext
from launcher.launcher_settings import LauncherSettings
from launcher.ui.behaviors.settingsbehavior import SettingsBehavior


class VideoSyncCheckBox(fsui.CheckBox):
    def __init__(self, parent):
        super().__init__(parent, gettext("V-Sync"))
        self.set_tooltip(gettext(
            "When checked, enable video synchronization whenever possible"))
        SettingsBehavior(self, ["video_sync"])

    def on_changed(self):
        LauncherSettings.set("video_sync", "1" if self.is_checked() else "")

    def on_video_sync_setting(self, value):
        self.check(value == "1")
