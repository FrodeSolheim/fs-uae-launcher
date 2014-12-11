from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import fsui as fsui
from ..I18N import gettext
from .SetupPanel import SetupPanel


class SetupDialog(fsui.Dialog):

    def __init__(self, parent):
        super().__init__(parent, gettext("Import Kickstarts"))
        buttons, layout = fsui.DialogButtons.create_with_layout(self)
        buttons.create_close_button()
        self.panel = SetupPanel(self)
        self.panel.set_min_width(620)
        layout.add(self.panel)
