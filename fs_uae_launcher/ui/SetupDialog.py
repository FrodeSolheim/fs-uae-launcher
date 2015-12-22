import fsui as fsui
from ..I18N import gettext
from .SetupPanel import SetupPanel


class SetupDialog(fsui.Window):

    def __init__(self, parent):
        super().__init__(parent, gettext("Import Kickstarts"))
        self.layout = fsui.VerticalLayout(padding=20)
        # buttons, layout = fsui.DialogButtons.create_with_layout(self)
        # buttons.create_close_button()
        self.panel = SetupPanel(self)
        self.panel.set_min_width(620)
        self.layout.add(self.panel)
