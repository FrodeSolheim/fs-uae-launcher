import fsui
from launcher.i18n import gettext
from launcher.ui.config.CustomOptionsPage import CustomOptionsPage
from launcher.ui.skin import LauncherTheme


class ConfigDialog(fsui.DialogWindow):
    def __init__(self, parent):
        title = gettext("Custom Configuration")
        super().__init__(parent, title=title)
        self.theme = LauncherTheme.get()
        if self.window.theme.has_close_buttons:
            buttons, layout = fsui.DialogButtons.create_with_layout(self)
            buttons.create_close_button()
        else:
            self.layout = fsui.VerticalLayout()
            self.layout.set_padding(20)
            layout = self.layout
        layout.add(CustomOptionsPage(self), fill=True, expand=True)

    @classmethod
    def run(cls, parent):
        cls(parent).show()
