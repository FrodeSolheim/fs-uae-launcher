import fsui
from ...I18N import gettext
from .CustomOptionsPage import CustomOptionsPage


class ConfigDialog(fsui.Dialog):

    def __init__(self, parent):
        super().__init__(parent, gettext("Custom Configuration"))
        buttons, layout = fsui.DialogButtons.create_with_layout(self)
        buttons.create_close_button()
        layout.add(CustomOptionsPage(self), fill=True, expand=True)

    @classmethod
    def run(cls, parent):
        cls(parent).show()
