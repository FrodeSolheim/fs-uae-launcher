import fsui as fsui
from .ExpansionsGroup import ExpansionsGroup
from ..Skin import Skin
from launcher.options import Option
from .configoptionui import ConfigOptionUI


class ConfigPanel(fsui.Panel):

    def __init__(self, parent):
        fsui.Panel.__init__(self, parent)
        Skin.set_background_color(self)

        # self.panel = fsui.Panel(self)
        # self.set_widget(self.panel)

        # self.expansions_group = ExpansionsGroup(self.panel)

        self.layout = fsui.VerticalLayout()
        # self.panel.layout.add(self.expansions_group, fill=True)

    def add_option(self, name):
        self.layout.add(ConfigOptionUI.create_group(self, name),
                        fill=True, margin=10)
