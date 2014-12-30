import fsui as fsui
from ...I18N import gettext
from ..settings.FullscreenToggleButton import FullscreenToggleButton


class LaunchGroup(fsui.Group):

    def __init__(self, parent):
        fsui.Group.__init__(self, parent)
        self.layout = fsui.HorizontalLayout()

        self.fullscreen_button = FullscreenToggleButton(self)
        self.layout.add(self.fullscreen_button, fill=True)

        self.layout.add_spacer(0, expand=True)

        self.start_button = fsui.Button(parent, gettext("Start"))
        self.start_button.activated.connect(self.on_start_button)
        self.layout.add(self.start_button, margin_left=10)

    def on_start_button(self):
        from ...FSUAELauncher import FSUAELauncher
        FSUAELauncher.start_game()
