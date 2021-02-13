from fsbc.application import app
from fsui import Image, ImageButton
from launcher.i18n import gettext
from launcher.launcher_settings import LauncherSettings


class VolumeButtonBase:
    """Mixin class also used by the workspace/titlebar fullscreen button."""

    def __init__(self, parent, icons):
        print("FullscreenToggle.__init__")
        super().__init__(parent, icons)
        self.icons = icons
        self.tooltip_text = gettext("Set the initial volume for the emulator")
        self.fullscreen_mode = False
        self.on_setting("volume", app.settings["volume"], initial=True)
        LauncherSettings.add_listener(self)

    def on_activate(self):
        if self.volume == 100:
            app.settings["volume"] = "0"
        elif self.volume == 0:
            app.settings["volume"] = "33"
        elif self.volume == 33:
            app.settings["volume"] = "66"
        else:
            app.settings["volume"] = "100"

    def on_destroy(self):
        LauncherSettings.remove_listener(self)
        super().on_destroy()

    def on_setting(self, key, value, initial=False):
        if key == "volume":
            try:
                self.volume = int(value)
            except ValueError:
                self.volume = 100
            if self.volume == 100:
                icon = self.icons[0]
            elif self.volume == 0:
                icon = self.icons[3]
            elif self.volume < 50:
                # In case volume is manually set to somewhere between the fixed
                # values supported by this button
                icon = self.icons[2]
            else:
                icon = self.icons[1]
            self.__set_image(icon, initial=initial)

    def __set_image(self, image, initial):
        if not initial:
            # pylint: disable=no-member
            self.set_image(image)


class ButtonWrapper(ImageButton):
    def __init__(self, parent, icons):
        super().__init__(parent, icons[0])


class VolumeButton(VolumeButtonBase, ButtonWrapper):
    def __init__(self, parent):
        super().__init__(
            parent,
            [
                Image(
                    "launcher:res/icons/audio-volume-high_16/audio-volume-high.png"
                ),
                Image(
                    "launcher:res/icons/audio-volume-medium_16/audio-volume-medium.png"
                ),
                Image(
                    "launcher:res/icons/audio-volume-low_16/audio-volume-low.png"
                ),
                Image(
                    "launcher:res/icons/audio-volume-muted_16/audio-volume-muted.png"
                ),
            ],
        )
        self.set_tooltip(self.tooltip_text)
        self.set_min_width(40)


# class VolumeButton(ImageButton):
#     def __init__(self, parent):
#         # self.volume_muted_icon = Image("launcher:res/windowed_16.png")
#         # self.volume_half_icon = Image("launcher:res/windowed_16.png")
#         # FIXME: Start with empty icon?
#         super().__init__(parent, Image.create_blank(16, 16))
#         # super().__init__(parent, self.volume_full_icon)
#         self.high_icon = Image(
#             "launcher:res/icons/audio-volume-high_16/audio-volume-high.png"
#         )
#         self.medium_icon = Image(
#             "launcher:res/icons/audio-volume-medium_16/audio-volume-medium.png"
#         )
#         self.low_icon = Image(
#             "launcher:res/icons/audio-volume-low_16/audio-volume-low.png"
#         )
#         self.muted_icon = Image(
#             "launcher:res/icons/audio-volume-muted_16/audio-volume-muted.png"
#         )
#         self.set_tooltip(gettext("Set the initial volume for the emulator"))
#         self.set_min_width(40)
#         # self.fullscreen_mode = False
#         self.volume = 100
#         self.on_setting("volume", app.settings["volume"])
#         LauncherSettings.add_listener(self)

#     def on_destroy(self):
#         LauncherSettings.remove_listener(self)
#         super().on_destroy()

#     def on_setting(self, key, value):
#         if key == "volume":
#             try:
#                 self.volume = int(value)
#             except ValueError:
#                 self.volume = 100
#             if self.volume == 100:
#                 icon = self.high_icon
#             elif self.volume == 0:
#                 icon = self.muted_icon
#             elif self.volume < 50:
#                 # In case volume is manually set to somewhere between the fixed
#                 # values supported by this button
#                 icon = self.low_icon
#             else:
#                 icon = self.medium_icon
#             self.set_image(icon)

#     def on_activate(self):
#         if self.volume == 100:
#             app.settings["volume"] = "0"
#         elif self.volume == 0:
#             app.settings["volume"] = "33"
#         elif self.volume == 33:
#             app.settings["volume"] = "66"
#         else:
#             app.settings["volume"] = "100"
