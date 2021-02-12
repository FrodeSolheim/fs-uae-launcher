import fsui
from launcher.context import get_launcher_theme
from .titlebar import TitleBar


class Window(fsui.Window):
    def __init__(
        self,
        parent,
        *,
        title="",
        size=None,
        menu=False,
        maximizable=True,
        minimizable=True,
        escape=False
    ):
        self.theme = get_launcher_theme(self)
        window_parent = None
        # window_parent = parent
        border = self.theme.titlebar_system()
        super().__init__(
            window_parent,
            title,
            border=border,
            maximizable=maximizable,
            minimizable=minimizable,
            escape=escape,
        )
        if size is not None:
            self.set_size(size)
        self.layout = fsui.VerticalLayout()

        use_border = False
        if use_border:
            self.layout.set_padding(1, 1, 1, 1)
            self.borderwidget = fsui.Panel(self)
            self.borderwidget.set_background_color(fsui.Color(0xCCD6E4))
        else:
            self.borderwidget = None

        self.set_background_color(self.theme.window_bgcolor())
        if not self.theme.titlebar_system():
            self.__titlebar = TitleBar(
                self,
                title=title,
                menu=menu,
                minimizable=minimizable,
                maximizable=maximizable,
            )
            self.layout.add(self.__titlebar, fill=True)

    def on_resize(self):
        if self.borderwidget:
            w, h = self.size()
            self.borderwidget.set_position_and_size((0, 0), (w, h))
        super().on_resize()
