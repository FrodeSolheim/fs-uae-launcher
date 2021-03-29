from launcher.ws.shell import (  # shell_name,
    shell_basename,
    shell_join,
    shell_listdir,
    shell_realcase,
)
from launcher.ws.wsiconview import WSIconView
from launcher.ws.wsiconwidget import WSIconWidget
from system.classes.window import Window
from system.classes.windowresizehandle import WindowResizeHandle


class ShellWindow(Window):
    def __init__(self, parent, path):
        self.path = shell_realcase(path)
        print("ShellWindow path =", self.path, "parent =", parent)
        name = shell_basename(self.path)
        if name.endswith(":"):
            name = name[:-1]

        width = WSIconWidget.ICON_WIDGET_WIDTH * 6 + 20 + 20
        height = WSIconWidget.ICON_WIDGET_HEIGHT * 4 + 40 + 20 + 10

        super().__init__(
            parent,
            title=name,
            size=(width, height),
        )
        # self.set_background_color(fsui.Color(0x808080))
        # self.set_background_color(fsui.Color(0xAEAEAE))

        # self.layout.padding_left = 20
        self.iconview = WSIconView(self)
        self.layout.add(self.iconview, expand=True, fill=True)

        for entry in shell_listdir(self.path):
            entry_lower = entry.lower()
            if entry_lower.endswith(".info"):
                if self.path.endswith(":") and entry_lower == "disk.info":
                    # Skip showing Disk.info for volumes.
                    continue
                name = entry[:-5]
                if self.path.lower().startswith("system:"):
                    self.iconview.add_launcher_icon(
                        shell_join(self.path, name)
                    )
                else:
                    self.iconview.add_shell_icon(shell_join(self.path, entry))

        self.layout_icons()

        WindowResizeHandle(self)

    def layout_icons(self):
        self.iconview.layout_icons()
