import fsui as fsui
from .config.KickstartGroup import KickstartGroup
from .config.MemoryGroup import MemoryGroup
from .config.ExpansionsGroup import ExpansionsGroup
from .Skin import Skin


class ExpansionsPanel(fsui.VerticalScrollArea):

    def __init__(self, parent):
        fsui.VerticalScrollArea.__init__(self, parent)
        Skin.set_background_color(self)

        panel = fsui.Panel(self)
        self.set_widget(panel)

        self.expansions_group = ExpansionsGroup(panel)

        panel.layout = fsui.VerticalLayout()
        panel.layout.add(self.expansions_group, fill=True)
