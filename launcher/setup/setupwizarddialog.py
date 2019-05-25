import fsui
from launcher.i18n import gettext
from launcher.setup.setupwelcomepage import SetupWelcomePage
from launcher.ui.skin import LauncherTheme
from launcher.ui.widgets import PrevButton, NextButton, CloseButton


class SetupWizardDialog(fsui.Window):
    @classmethod
    def open(cls, parent=None):
        return fsui.open_window_instance(cls, parent)

    def __init__(self, parent):
        super().__init__(
            parent,
            gettext("Setup Wizard"),
            minimizable=False,
            maximizable=False,
        )
        self.theme = LauncherTheme.get()
        self.layout = fsui.VerticalLayout()

        page = SetupWelcomePage(self)
        self.layout.add(page, expand=True, fill=True)

        button_layout = fsui.HorizontalLayout()
        self.layout.add(button_layout, fill=True, margin=20)
        button_layout.add_spacer(0, expand=True)
        self.prev_button = PrevButton(self)
        button_layout.add(self.prev_button, fill=True, margin_left=10)
        self.next_button = NextButton(self)
        button_layout.add(self.next_button, fill=True, margin_left=10)
        if self.window.theme.has_close_buttons:
            self.close_button = CloseButton(self)
            button_layout.add(self.close_button, fill=True, margin_left=10)
