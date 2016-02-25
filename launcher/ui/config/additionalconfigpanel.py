import fsui
from launcher.i18n import gettext
from launcher.options import Option
from launcher.ui.config.configpanel import ConfigPanel
from .ConfigDialog import ConfigDialog


class AdditionalConfigPanel(ConfigPanel):

    def __init__(self, parent):
        ConfigPanel.__init__(self, parent)

        hori_layout = fsui.HorizontalLayout()
        self.layout.add(hori_layout, fill=True)

        heading_label = fsui.HeadingLabel(
            self, gettext("Additional Configuration"))
        hori_layout.add(heading_label, margin=10)
        hori_layout.add_spacer(0, expand=True)

        self.custom_button = fsui.Button(
            self, gettext("Custom Configuration") + "...")
        self.custom_button.activated.connect(self.on_custom_button)
        hori_layout.add(self.custom_button, margin_right=10)

        self.layout.add_spacer(0)

        self.add_option(Option.CPU)
        self.add_option(Option.FLOPPY_DRIVE_SPEED)
        self.add_option(Option.FLOPPY_DRIVE_COUNT)
        self.add_option(Option.CDROM_DRIVE_COUNT)
        # self.add_option(Option.DONGLE_TYPE)

        self.layout.add_spacer(10)
        heading_label = fsui.HeadingLabel(self, gettext("Deprecated Options"))
        self.layout.add(heading_label, margin=10)
        self.layout.add_spacer(0)

        self.add_option(Option.UAEGFX_CARD)

    def on_custom_button(self):
        ConfigDialog.run(self.get_window())
