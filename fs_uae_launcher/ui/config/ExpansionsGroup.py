import fsui as fsui
from ...I18N import gettext
from .ConfigCheckBox import ConfigCheckBox
from ..HelpButton import HelpButton


class ExpansionsGroup(fsui.Group):

    def __init__(self, parent):
        fsui.Group.__init__(self, parent)
        self.layout = fsui.VerticalLayout()

        heading_label = fsui.HeadingLabel(self, gettext("Expansions"))
        self.layout.add(heading_label, margin=10)
        self.layout.add_spacer(0)

        hori_layout = fsui.HorizontalLayout()
        self.layout.add(hori_layout, fill=True)

        vert_layout = fsui.VerticalLayout()
        hori_layout.add(vert_layout, fill=True, expand=True)

        hor2_layout = fsui.HorizontalLayout()
        widget = ConfigCheckBox(self, gettext("Picasso96 Support"),
                                "uaegfx_card")
        widget.set_tooltip(gettext("Picasso96 Support (uaegfx.card)"))
        hor2_layout.add(widget, expand=True)
        widget = HelpButton(self, "http://fs-uae.net/options#uaegfx-card")
        hor2_layout.add(widget, margin_left=10)
        vert_layout.add(hor2_layout, fill=True, margin=10)

        # vert_layout = fsui.VerticalLayout()
        # hori_layout.add(vert_layout, fill=True, expand=True)

        hor2_layout = fsui.HorizontalLayout()
        widget = ConfigCheckBox(self, gettext("Built-in TCP/IP Stack"),
                                "bsdsocket_library")
        widget.set_tooltip(
            gettext("Built-in TCP/IP Stack (bsdsocket.library)"))
        hor2_layout.add(widget, expand=True)
        widget = HelpButton(
            self, "http://fs-uae.net/options#bsdsocket-library")
        hor2_layout.add(widget, margin_left=10)
        vert_layout.add(hor2_layout, fill=True, margin=10)
