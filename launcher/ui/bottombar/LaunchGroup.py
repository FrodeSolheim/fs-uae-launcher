from fsgs.runner import GameRunner
import fsui as fsui
from launcher.i18n import gettext
from launcher.launcher_settings import LauncherSettings
from launcher.ui.behaviors.settingsbehavior import SettingsBehavior
from launcher.ui.settings.fullscreen_toggle_button import FullscreenToggleButton
from launcher.ui.settings.fullscreen_mode_button import FullscreenModeButton
from launcher.ui.settings.monitor_button import MonitorButton
from launcher.ui.settings.override_warning import OverrideWarning
from launcher.ui.settings.video_sync_checkbox import VideoSyncCheckBox


class LaunchGroup(fsui.Group):

    def __init__(self, parent, add_label=False):
        fsui.Group.__init__(self, parent)
        self.layout = fsui.VerticalLayout()
        if add_label:
            label = fsui.Label(self, gettext("Launch FS-UAE"))
            self.layout.add(label)

        self.hori_layout = fsui.HorizontalLayout()
        self.layout.add(self.hori_layout, fill=True, expand=True)

        self.hori_layout.add(
            FullscreenModeButton(self), fill=True, margin_right=10)
        self.hori_layout.add(MonitorButton(self), fill=True, margin_right=10)
        self.hori_layout.add(
            ScreenInfoLabel(parent), fill=True, expand=True, margin_right=10)
        # self.hori_layout.add_spacer(0, expand=True)

        self.hori_layout.add(VideoSyncCheckBox(parent), margin_right=10)

        self.hori_layout.add(OverrideWarning(self, "fullscreen"),
                             margin_right=10)
        self.hori_layout.add(FullscreenToggleButton(self), fill=True)

        self.start_button = fsui.Button(parent, gettext("Start"))
        self.start_button.activated.connect(self.on_start_button)
        self.hori_layout.add(self.start_button, fill=True, margin_left=10)

        # SettingsBehavior(self, ["fullscreen"])

    def on_start_button(self):
        from ...fs_uae_launcher import FSUAELauncher
        FSUAELauncher.start_game()

    # def on_fullscreen_config(self, _):
    #     self.hori_layout.update()

    def set_min_height(self, height):
        pass


class ScreenInfoLabel(fsui.Label):

    def __init__(self, parent):
        super().__init__(parent, "")
        try:
            from fsui.qt import init_qt
            qapplication = init_qt()
        except AttributeError:
            pass
        else:
            for screen in qapplication.screens():
                screen.geometryChanged.connect(self.on_screen_change)
                screen.refreshRateChanged.connect(self.on_screen_change)
            qapplication.screenAdded.connect(self.on_screen_added)
        SettingsBehavior(self, ["fullscreen", "monitor", "assume_refresh_rate"])

    def on_fullscreen_setting(self, _):
        self.update_info()

    def on_screen_change(self, _):
        print("-- screen changed --")
        self.update_info()

    def on_screen_added(self, screen):
        print("-- screen added --")
        screen.geometryChanged.connect(self.on_screen_change)
        screen.refreshRateChanged.connect(self.on_screen_change)
        self.update_info()

    def on_assume_refresh_rate_setting(self, _):
        self.update_info()

    def on_monitor_setting(self, value):
        self.update_info(value=value)

    def update_info(self, value=None):
        if LauncherSettings.get("fullscreen") != "1":
            self.set_text("")
            return
        if value is None:
            value = LauncherSettings.get("monitor")
        x, y, w, h = GameRunner.screen_rect_for_monitor(value)
        # index = GameRunner.screen_index_for_monitor(value)
        refresh_rate = GameRunner.screen_refresh_rate_for_monitor(value)
        assume_refresh_rate = LauncherSettings.get("assume_refresh_rate")
        if assume_refresh_rate:
            refresh_rate_override = " (OVERRIDING {})".format(refresh_rate)
            try:
                refresh_rate = float(assume_refresh_rate)
            except ValueError:
                refresh_rate = 0.0
        else:
            refresh_rate_override = ""
        if x or y:
            pos_str = " ({}, {})".format(x, y)
        else:
            pos_str = ""
        self.set_text("{}x{}{} @ {}Hz{}".format(
            w, h, pos_str, refresh_rate, refresh_rate_override))
