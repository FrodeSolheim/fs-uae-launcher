from fs_uae_launcher.ui.behaviors.configbehavior import ConfigBehavior
from fs_uae_launcher.ui.settings.overridewarning import OverrideWarning
import fsui as fsui
from ...I18N import gettext
from ..settings.FullscreenToggleButton import FullscreenToggleButton


class LaunchGroup(fsui.Group):

    def __init__(self, parent, add_label=False):
        fsui.Group.__init__(self, parent)
        self.layout = fsui.VerticalLayout()
        if add_label:
            label = fsui.Label(self, gettext("Launch FS-UAE"))
            self.layout.add(label)

        self.hori_layout = fsui.HorizontalLayout()
        self.layout.add(self.hori_layout, fill=True, expand=True)

        self.hori_layout.add_spacer(0, expand=True)

        self.hori_layout.add(OverrideWarning(self, "fullscreen"),
                             margin_right=10)
        self.hori_layout.add(FullscreenToggleButton(self), fill=True)

        self.start_button = fsui.Button(parent, gettext("Start"))
        self.start_button.activated.connect(self.on_start_button)
        self.hori_layout.add(self.start_button, fill=True, margin_left=10)

        ConfigBehavior(self, ["fullscreen"])

    def on_start_button(self):
        from ...FSUAELauncher import FSUAELauncher
        FSUAELauncher.start_game()

    def on_fullscreen_config(self, value):
        self.hori_layout.update()

    def set_min_height(self, height):
        pass
