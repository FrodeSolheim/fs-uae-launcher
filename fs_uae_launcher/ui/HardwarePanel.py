import fsui as fsui
from .config.KickstartGroup import KickstartGroup
from .config.MemoryGroup import MemoryGroup
from .config.ExpansionsGroup import ExpansionsGroup
from .Skin import Skin


class HardwarePanel(fsui.VerticalScrollArea):

    def __init__(self, parent):
        fsui.VerticalScrollArea.__init__(self, parent)
        Skin.set_background_color(self)

        # self.scroll_area = fsui.VerticalScrollArea(self)
        # self.layout = fsui.VerticalLayout()
        # self.layout.add(self.scroll_area, expand=True, fill=True)

        # panel = fsui.Panel(self.scroll_area)
        panel = fsui.Panel(self)
        # self.scroll_area.set_widget(panel)
        self.set_widget(panel)

        self.kickstart_group = KickstartGroup(panel)
        self.memory_group = MemoryGroup(panel)
        # self.expansions_group = ExpansionsGroup(panel)

        panel.layout = fsui.VerticalLayout()
        panel.layout.add(self.kickstart_group, fill=True)
        panel.layout.add_spacer(10)
        panel.layout.add_spacer(Skin.EXTRA_GROUP_MARGIN)
        panel.layout.add(self.memory_group, fill=True)
        # panel.layout.add_spacer(Skin.EXTRA_GROUP_MARGIN)
        # panel.layout.add(self.expansions_group, fill=True)
