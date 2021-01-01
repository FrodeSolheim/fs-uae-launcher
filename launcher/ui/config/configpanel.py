from fsui import Color, Panel, VerticalLayout
from launcher.ui.behaviors.platformbehavior import AMIGA_PLATFORMS
from launcher.ui.options import ConfigWidgetFactory

# from launcher.ui.skin import Skin


class ConfigPanel(Panel):
    def __init__(self, parent):
        super().__init__(parent)
        # Skin.set_background_color(self)
        self.layout = VerticalLayout()
        self.config_widget_factory = ConfigWidgetFactory()

        # FIXME: Why is it necessary to set a transparent color here? Shouldn't
        # it be sufficient to let the panel have its autoFillBackground set
        # to False (default)?
        # self.set_background_color(Color(0, 0, 0, 0))
        # self.set_background_color(Color(255, 0, 0))

    def add_option(self, name, fill=True):
        self.layout.add(
            self.config_widget_factory.create(self, name),
            fill=fill,
            margin=10,
            margin_bottom=0,
        )

    def add_amiga_option(self, name, fill=True, parent=None):
        if parent is None:
            parent = self
        parent.layout.add(
            self.config_widget_factory.create(
                parent, name, platforms=AMIGA_PLATFORMS
            ),
            fill=fill,
            margin=10,
            margin_bottom=0,
        )
