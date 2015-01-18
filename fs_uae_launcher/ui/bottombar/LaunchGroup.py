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

        hor_layout = fsui.HorizontalLayout()
        self.layout.add(hor_layout, fill=True, expand=True)

        self.fullscreen_button = FullscreenToggleButton(self)
        hor_layout.add(self.fullscreen_button, fill=True)

        hor_layout.add_spacer(0, expand=True)

        self.start_button = fsui.Button(parent, gettext("Start"))
        self.start_button.activated.connect(self.on_start_button)
        hor_layout.add(self.start_button, fill=True, margin_left=10)

    def on_start_button(self):
        from ...FSUAELauncher import FSUAELauncher
        FSUAELauncher.start_game()

    def set_min_height(self, height):
        pass
