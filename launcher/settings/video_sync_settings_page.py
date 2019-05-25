import fsui
from launcher.i18n import gettext
from launcher.launcher_settings import LauncherSettings
from launcher.settings.settings_page import SettingsPage


class VideoSyncSettingsPage(SettingsPage):
    def __init__(self, parent):
        super().__init__(parent)
        icon = fsui.Icon("video-settings", "pkg:workspace")
        gettext("Video Synchronization Settings")
        title = gettext("Synchronization")
        subtitle = gettext(
            "Synchronize FS-UAE with your display for " "smooth video"
        )
        self.add_header(icon, title, subtitle)

        label = fsui.MultiLineLabel(
            self,
            gettext(
                "Enabling the following option will synchronize the emulation "
                "to the display when the emulation refresh rate matches the"
                "screen refresh rate."
            ),
            640,
        )
        self.layout.add(label, fill=True, margin_top=0)
        self.video_sync_group = self.add_option("video_sync")

        self.low_latency_group = self.add_option("low_latency_vsync")

        # label = fsui.MultiLineLabel(self, gettext(
        #     "Enabling the following option will prevent tearing from "
        #     "occurring, but will also use more CPU. Input latency "
        #     "may become slightly higher."), 640)
        # self.layout.add(label, fill=True, margin_top=0)
        # self.vblank_checkbox = fsui.HeadingCheckBox(self, gettext(
        #     "Synchronize buffer swaps with display (prevents tearing)"))
        # self.layout.add(self.vblank_checkbox, margin_top=20)

        self.sync_method_label = fsui.MultiLineLabel(
            self,
            gettext(
                "Depending on your OS and OpenGL drivers, synchronizing "
                "can use needlessly much CPU (esp. applies to "
                "Linux). You can experiment with different sync methods "
                "to improve performance."
            ),
            640,
        )
        self.layout.add(self.sync_method_label, fill=True, margin_top=20)
        self.sync_method_group = self.add_option("video_sync_method")

        # self.smooth_label = fsui.MultiLineLabel(self, gettext(
        #     "In order to get really smooth Amiga graphics, you need to "
        #     "enable the following option, and also make sure your display "
        #     "is running at 50Hz (for PAL) or 60Hz (for NTSC)."), 640)
        # self.layout.add(self.smooth_label, fill=True, margin_top=20)
        # self.full_sync_checkbox = fsui.HeadingCheckBox(self, gettext(
        #     "Also synchronize emulation with display when possible "
        #     "(smooth scrolling)"))
        # self.layout.add(self.full_sync_checkbox, margin_top=20)

        self.layout.add_spacer(0, expand=True)

        hori_layout = fsui.HorizontalLayout()
        self.layout.add(hori_layout, fill=True, margin_top=10)
        hori_layout.add(
            fsui.ImageView(
                self, fsui.Image("launcher:res/16x16/world_link.png")
            )
        )
        label = fsui.URLLabel(
            self,
            gettext("How to achieve perfectly smooth scrolling"),
            "https://fs-uae.net/perfectly-smooth-scrolling",
        )
        hori_layout.add(label, margin_left=6)

        text = gettext(
            "Synchronizing with the display can in some cases cause "
            "increased stuttering and low frame rates (esp. in some Linux "
            "desktop environments with compositing enabled)."
        )
        link = (
            " <a href='https://fs-uae.net/video-synchronization-issues'>"
            "{0}</a>.".format(gettext("Read more"))
        )

        label = fsui.MultiLineLabel(self, text + link, min_width=640)
        self.layout.add(label, fill=True, margin_top=20)

        LauncherSettings.add_listener(self)
        for key in ["video_sync"]:
            self.on_setting(key, LauncherSettings.get(key))

        # self.vblank_checkbox.changed.connect(self.on_vblank_changed)
        # self.full_sync_checkbox.changed.connect(self.on_full_sync_changed)

    def on_destroy(self):
        LauncherSettings.remove_listener(self)

    def on_setting(self, key, _):
        if key == "video_sync":
            # value = value.lower()
            # self.vblank_checkbox.check(value in ["auto", "full", "vblank"])
            # self.full_sync_checkbox.check(value in ["auto", "full"])
            self.update_widgets()

    # def on_vblank_changed(self):
    #     self.on_either_checkbox_changed()
    #
    # def on_full_sync_changed(self):
    #     self.on_either_checkbox_changed()
    #
    # def on_either_checkbox_changed(self):
    #     value = ""
    #     if self.vblank_checkbox.is_checked():
    #         if self.full_sync_checkbox.is_checked():
    #             value = "auto"
    #         else:
    #             value = "vblank"
    #     LauncherSettings.set("video_sync", value)

    def update_widgets(self):
        value = LauncherSettings.get("video_sync")
        vblank = value in ["1", "auto", "full", "vblank"]
        full = value in ["1", "auto", "full"]

        # self.full_sync_checkbox.enable(vblank)
        self.sync_method_group.label.enable(vblank)
        self.sync_method_group.widget.enable(vblank)
        self.sync_method_group.help_button.enable(vblank)
        self.sync_method_label.enable(vblank)
        # self.smooth_label.enable(vblank)
        self.low_latency_group.label.enable(full)
        self.low_latency_group.widget.enable(full)
        self.low_latency_group.help_button.enable(full)
