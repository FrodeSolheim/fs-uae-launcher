from launcher.system.classes.window import Window
from fsgamesys.ogd.refresh import DatabaseRefreshTask
import fsui
from fsui import VerticalLayout
from fsui.extra.iconheader import IconHeader

# from workspace.shell import SimpleApplication
from launcher.res import gettext

# from launcher.ui.widgets import CloseButton
from workspace.ui.theme import WorkspaceTheme


class DatabaseUpdaterWindow(Window):
    def __init__(self, parent=None):
        print("DatabaseUpdaterWindow parent =", parent)
        title = gettext("Database updater")
        super().__init__(parent, title=title, maximizable=False)
        self.set_icon(fsui.Icon("refresh", "pkg:workspace"))
        self.theme = WorkspaceTheme.instance()

        self.layout.min_width = 500
        vert_layout = VerticalLayout()
        self.layout.add(vert_layout, fill=True, expand=True, margin=20)
        # self.layout.set_padding(20, 20, 20, 20)

        self.icon_header = IconHeader(
            self,
            fsui.Icon("refresh", "pkg:workspace"),
            gettext("Updating Database"),
            "",
        )
        vert_layout.add(self.icon_header, fill=True, margin_bottom=20)

        hori_layout = fsui.HorizontalLayout()
        vert_layout.add(hori_layout, fill=True)
        self.created_label = fsui.Label(self, "")
        hori_layout.add(self.created_label, expand=True)
        hori_layout.add_spacer(20)
        self.stop_button = fsui.Button(self, gettext("Stop"))
        self.stop_button.activated.connect(self.on_abort_activated)
        hori_layout.add(self.stop_button)

        # if self.window().theme.has_close_buttons:
        #     self.close_button = CloseButton(self)
        #     hori_layout.add(self.close_button, fill=True, margin_left=10)

        self.set_size(self.layout.get_min_size())
        self.center_on_parent()

        self.task = DatabaseRefreshTask()
        self.task.progressed.connect(self.on_progress)
        self.task.failed.connect(self.on_failure)
        self.task.succeeded.connect(self.close)
        self.task.stopped.connect(self.close)
        self.task.start()

        self.closed.connect(self.__on_closed)

    def __del__(self):
        print("DatabaseUpdaterWindow.__del__")

    # def on_close(self):
    #     print("DatabaseUpdaterWindow.on_close")
    #     self.task.stop()

    def __on_closed(self):
        self.task.stop()
        self.task.progressed.disconnect(self.on_progress)
        self.task.failed.disconnect(self.on_failure)
        self.task.succeeded.disconnect(self.close)
        self.task.stopped.disconnect(self.close)

    def on_abort_activated(self):
        self.task.stop()
        self.stop_button.set_enabled(False)

    def on_failure(self, message):
        fsui.show_error(message, parent=self.get_window())

    def on_progress(self, message):
        if not isinstance(message, str):
            message = message[0]
        # print("on_progress", status)
        self.icon_header.subtitle_label.set_text(message)
