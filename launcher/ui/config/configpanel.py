from fsui import Panel, VerticalLayout
from launcher.ui.behaviors.platformbehavior import AMIGA_PLATFORMS
from launcher.ui.skin import Skin
from launcher.ui.options import ConfigWidgetFactory


class ConfigPanel(Panel):
    def __init__(self, parent):
        super().__init__(parent)
        Skin.set_background_color(self)
        self.layout = VerticalLayout()
        self.config_widget_factory = ConfigWidgetFactory()

    def add_option(self, name, fill=True):
        self.layout.add(self.config_widget_factory.create(
            self, name), fill=fill, margin=10, margin_bottom=0)

    def add_amiga_option(self, name, fill=True):
        self.layout.add(self.config_widget_factory.create(
            self, name, platforms=AMIGA_PLATFORMS),
            fill=fill, margin=10, margin_bottom=0)
