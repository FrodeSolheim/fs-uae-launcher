import fsui as fsui
from ...I18N import gettext
from .MemoryWidget import MemoryWidget


class MemoryGroup(fsui.Group):

    def __init__(self, parent):
        fsui.Group.__init__(self, parent)
        self.layout = fsui.VerticalLayout()

        gettext("Memory")
        gettext("Memory Configuration")
        heading_label = fsui.HeadingLabel(
            self, gettext("Override Installed Memory"))
        self.layout.add(heading_label, margin=10)
        self.layout.add_spacer(0)

        # hori_layout = fsui.HorizontalLayout()
        # self.layout.add(hori_layout, fill=True)

        vert_layout = fsui.VerticalLayout()
        # hori_layout.add(vert_layout, fill=True, expand=-1)
        self.layout.add(vert_layout, fill=True)

        widget = MemoryWidget(
            self, gettext("Chip RAM"), "chip_memory",
            [256, 512, 1024, 1536, 2048, 4096, 8192])
        vert_layout.add(widget, fill=True, margin=10)

        widget = MemoryWidget(self, gettext("Slow RAM"), "slow_memory",
                              [0, 512, 1024, 1536, 1792])
        vert_layout.add(widget, fill=True, margin=10)

        # vert_layout = fsui.VerticalLayout()
        # hori_layout.add(vert_layout, fill=True, expand=-1)

        widget = MemoryWidget(
            self, gettext("Zorro II Fast RAM"), "fast_memory",
            [0, 64, 128, 256, 512, 1024, 2048, 4096, 8192])
        vert_layout.add(widget, fill=True, margin=10)

        widget = MemoryWidget(
            self, gettext("Zorro III Fast RAM"), "zorro_iii_memory",
            [0, 1024, 2048, 4096, 8192, 16384, 32768, 65536, 131072,
             262144, 393216, 524288, 786432, 1048576])
        vert_layout.add(widget, fill=True, margin=10)

        widget = MemoryWidget(
            self, gettext("Motherboard Fast RAM"), "motherboard_ram",
            [0, 1024, 2048, 4096, 8192, 16384, 32768, 65536])
        vert_layout.add(widget, fill=True, margin=10)
