import sys

import fsui
from fsgamesys.drivers.gamedriver import GameDriver
from launcher.context import get_config
from launcher.i18n import gettext
from launcher.launcher_settings import LauncherSettings
from launcher.option import Option
from launcher.settings.fullscreentogglebutton import FullscreenToggleButton
from launcher.settings.override_warning import OverrideWarning
from launcher.ui2.startbutton import StartButton
from launcher.ui.behaviors.settingsbehavior import SettingsBehavior


class LaunchGroup(fsui.Group):
    def __init__(self, parent, gsc):
        super().__init__(parent)
        self.layout = fsui.VerticalLayout()
        self.hori_layout = fsui.HorizontalLayout()
        self.layout.add(self.hori_layout, fill=True, expand=True)
        self.progress_label = fsui.Label(self, "")
        self.progress_label.set_visible(False)
        self.hori_layout.add(self.progress_label, fill=True, expand=True)

        # self.progress_2_label = fsui.Label(self, "")
        # self.progress_2_label.set_visible(False)
        # self.hori_layout.add(self.progress_2_label, fill=True, expand=True)

        # self.fullscreen_mode_button = FullscreenModeButton(self)
        # self.hori_layout.add(
        #     self.fullscreen_mode_button, fill=True, margin_right=10)
        # self.monitor_button = MonitorButton(self)
        # self.hori_layout.add(
        #     self.monitor_button, fill=True, margin_right=10)

        self.screen_info_label = ScreenInfoLabel(self)
        self.hori_layout.add(
            self.screen_info_label, fill=True, expand=True, margin_right=10
        )
        # self.video_sync_checkbox = VideoSyncCheckBox(self)
        # self.hori_layout.add(self.video_sync_checkbox, margin_right=10)
        self.override_warning = OverrideWarning(self, Option.FULLSCREEN)
        self.hori_layout.add(self.override_warning, margin_right=10)
        self.fullscreen_button = FullscreenToggleButton(self)
        self.hori_layout.add(self.fullscreen_button, fill=True)
        start_button = StartButton(self)
        self.hori_layout.add(start_button, fill=True, margin_left=10)
        # ConfigBehavior(self, [Option.FULLSCREEN])
        gsc.config.add_behavior(
            self, [Option.FULLSCREEN, "__running", "__progress"]
        )

    def on___running_config(self, value):
        widgets = [
            # self.fullscreen_mode_button,
            # self.monitor_button,
            self.screen_info_label,
            # self.video_sync_checkbox,
            self.fullscreen_button,
        ]
        for widget in widgets:
            widget.set_visible(value != "1")
        self.progress_label.set_visible(value == "1")
        # self.progress_2_label.set_visible(value == "1")
        self.hori_layout.update()

    def on___progress_config(self, value):
        # first, rest = value.split(":", 1)
        # self.progress_label.set_text(first)
        # self.progress_2_label.set_text(rest.strip())
        self.progress_label.set_text(value)

    def on_fullscreen_config(self, _):
        self.layout.update()


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
        SettingsBehavior(
            self, ["fullscreen", "monitor", "assume_refresh_rate"]
        )

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
        x, y, w, h = GameDriver.screen_rect_for_monitor(value)
        # index = GameRunner.screen_index_for_monitor(value)
        refresh_rate = GameDriver.screen_refresh_rate_for_monitor(value)
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
        self.set_text(
            "{}x{}{} @ {}Hz{}".format(
                w, h, pos_str, refresh_rate, refresh_rate_override
            )
        )


class LaunchDialog(fsui.Window):
    def __init__(self, parent, title, task, *, gscontext):
        print("LaunchDialog parent =", parent)
        self.gscontext = gscontext

        self.has_parent = parent is not None
        self.no_gui = "--no-gui" in sys.argv
        super().__init__(parent, title, maximizable=False)
        self.layout = fsui.VerticalLayout()

        self.layout.add_spacer(400, 20)

        hor_layout = fsui.HorizontalLayout()
        self.layout.add(hor_layout, fill=True)

        hor_layout.padding_right = 20
        hor_layout.add_spacer(20)

        image = fsui.Image("launcher:/data/fs_uae_group.png")
        self.image_view = fsui.ImageView(self, image)
        hor_layout.add(self.image_view, valign=0.0)
        hor_layout.add_spacer(20)

        ver_layout = fsui.VerticalLayout()
        hor_layout.add(ver_layout, fill=True, expand=True)
        self.title_label = fsui.HeadingLabel(self, title)
        ver_layout.add(self.title_label, fill=True)

        ver_layout.add_spacer(6)
        self.sub_title_label = fsui.Label(self, gettext("Preparing..."))
        ver_layout.add(self.sub_title_label, fill=True)

        self.layout.add_spacer(20)

        hor_layout = fsui.HorizontalLayout()
        self.layout.add(hor_layout, fill=True)

        hor_layout.add_spacer(20, expand=True)
        self.cancel_button = fsui.Button(self, gettext("Cancel"))
        self.cancel_button.activated.connect(self.on_cancel_button)
        hor_layout.add(self.cancel_button)
        hor_layout.add_spacer(20)

        self.layout.add_spacer(20)
        self.set_size(self.layout.get_min_size())
        self.center_on_parent()

        self.was_closed = False
        self.task = task
        self.task.progressed.connect(self.on_progress)
        self.task.finished.connect(self.on_complete)
        self.task.failed.connect(self.on_error)

        self.closed.connect(self.__closed)

    def complete(self):
        print("TaskRunner.complete")
        # Setting task to None so destructors are run now
        self.task = None
        self.was_closed = True
        self.close()
        self.deleteLater()

    def __closed(self):
        get_config(self).set("__running", "")
        self.cancel()
        return False

    def on_progress(self, progress):
        def hide_function():
            self.set_visible(False)

        def function():
            if progress == "__run__":
                self.cancel_button.set_enabled(False)
                # Hide dialog after 1.5 seconds. The reason for delaying it
                # is to avoid "confusing" flickering if/when the dialog is
                # only shown for a split second.
                if self.visible():
                    fsui.call_later(1500, hide_function)
                get_config(self).set(
                    "__progress", gettext("Running: Emulator")
                )
            else:
                if self.no_gui:
                    print("[PROGRESS]", progress)
                else:
                    self.sub_title_label.set_text(progress)
                get_config(self).set(
                    "__progress", "Preparing: {}".format(progress)
                )

        fsui.call_after(function)

    def show(self, *args, **kwargs):
        if self.has_parent or self.no_gui:
            # Hack to prevent it from being shown
            pass
        else:
            self.center_on_screen()
            super().show()

    def on_complete(self):
        def function():
            self.complete()

        fsui.call_after(function)

    def on_error(self, message):
        fsui.show_error(message, title="Guru Meditation")
        self.close()

    def on_cancel_button(self):
        self.cancel()

    def cancel(self):
        print("LaunchDialog.cancel")
        if self.task is not None:
            self.task.stop()
        self.cancel_button.set_enabled(False)
