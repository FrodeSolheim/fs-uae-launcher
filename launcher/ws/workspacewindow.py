from fsgamesys.monitors.screens import screen_rects
from fsui import Color, Panel, VerticalLayout, Window
from launcher.context import get_launcher_theme
from launcher.ws.shell import shell_volumes
from launcher.ws.workspacemenu import WorkspaceMenu
from launcher.ws.workspacetitlebar import WorkspaceTitleBar
from launcher.ws.wsiconview import WSIconView
from launcher.settings import get_workspace_window_title

"""
Note: Qt.WindowStaysOnBottomHint is not implemented for macOS, so the
WorkspaceWindow cannot be force to the background on macOS :-/
"""


class BackgroundWidget(Panel):
    def __init__(self, parent):
        super().__init__(parent)
        self.set_background_color(Color(0xFF0000))
        from fsui.qt import QLabel, QParent, QPixmap

        self.label = QLabel(QParent(self))
        pixmap = QPixmap("data/Background.jpg")

        # self._qwidget.setStyleSheet("border: 0px;")
        # self._qwidget.setContentsMargins(0, 0, 0, 0)
        # self._qwidget.move(0, 0)

        # self.label.setAutoFillBackground(True)
        # p = self.label.palette()
        # p.setColor(self.label.backgroundRole(), QColor(255, 0, 0))
        # self.label.setPalette(p)

        self.label.setPixmap(pixmap)
        # self.label.setFrameShape(QFrame.NoFrame)
        # self.label.setLineWidth(0)
        self.label.setScaledContents(True)
        # self.label.setStyleSheet("border: 0px;")
        # self.label.setContentsMargins(0, 0, 0, 0)
        # self.label.move(0, 0)

    def on_resize(self):
        self.label.setFixedWidth(self.size()[0])
        self.label.setFixedHeight(self.size()[1])


class WorkspaceWindow(Window):
    def __init__(self, parent):
        super().__init__(
            parent,
            title=get_workspace_window_title(),
            border=False,
            below=True,
        )
        self.theme = get_launcher_theme(self)
        self.layout = VerticalLayout()

        self.background_widget = BackgroundWidget(self)
        self.layout.add(WorkspaceTitleBar(self), fill=True)

        # self.layout.padding_top = 300
        # self.layout.padding_right = 300
        # self.layout.padding_bottom = 300
        # self.layout.padding_left = 300

        self.set_background_color(self.theme.window_bgcolor())

        print("\n\nFIXME: Hardcoded to use rightmost screen\n\n")
        rect = screen_rects()[-1]
        self.set_position_and_size(
            (rect["x"], rect["y"]), (rect["w"], rect["h"])
        )
        # self.set_position((1920, 0))

        # self.layout.add_spacer(0, expand=True)

        # horilayout = HorizontalLayout()
        # self.layout.add(horilayout, fill=True)
        # button = Button(self, "Close")
        # button.activated.connect(self.close)
        # horilayout.add(button)
        # button = Button(self, "Prefs")
        # button.activated.connect(self.__prefs)
        # horilayout.add(button)

        self.iconview = WorkspaceIconView(self)
        self.layout.add(self.iconview, expand=True, fill=True)

        # self.layout.add(
        #     BottomDebugPanel(self, close=False, quit=True), fill=True
        # )

        # self.layout.add(button)
        # self.layout.update()

        # FIXME: self.show_maximized() ?
        # FIXME: If we set maximized before show, then the button does not
        # appear ?
        self.show()
        self.set_maximized(True)

    def on_menu(self):
        print("on_menu")
        return WorkspaceMenu(self)

    def on_resize(self):
        self.background_widget.set_position_and_size((0, 0), self.size())
        super().on_resize()


class WorkspaceIconView(WSIconView):
    def __init__(self, parent):
        super().__init__(
            parent, vertical_layout=True, textcolor=Color(0xFFFFFF)
        )
        for volume in shell_volumes():
            self.add_launcher_icon(volume)
