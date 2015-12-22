import fsui
from ...I18N import gettext
from .CustomOptionsPage import CustomOptionsPage


class ConfigDialog(fsui.Window):

    def __init__(self, parent):
        title = gettext("Custom Configuration")
        super().__init__(parent, title=title, minimizable=False,
                         maximizable=False)
        self.layout = fsui.VerticalLayout()
        self.layout.set_padding(20)
        # buttons, layout = fsui.DialogButtons.create_with_layout(self)
        # buttons.create_close_button()
        self.layout.add(CustomOptionsPage(self), fill=True, expand=True)

    @classmethod
    def run(cls, parent):
        cls(parent).show()
