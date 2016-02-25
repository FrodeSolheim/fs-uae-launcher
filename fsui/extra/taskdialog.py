import fsui
from fsui.extra.iconheader import IconHeader
from launcher.res import gettext


class TaskDialog(fsui.Window):

    def __init__(self, parent, task):
        fsui.Window.__init__(
            self, parent, task.get_task_name())
        self.set_icon(fsui.Icon("tools", "pkg:workspace"))

        self.layout = fsui.VerticalLayout()
        self.layout.min_width = 500
        self.layout.set_padding(20, 20, 20, 20)

        self.icon_header = IconHeader(
            self, fsui.Icon("tools", "pkg:workspace"),
            task.get_task_name(), "")
        self.layout.add(self.icon_header, fill=True, margin_bottom=20)

        hori_layout = fsui.HorizontalLayout()
        self.layout.add(hori_layout, fill=True)
        self.created_label = fsui.Label(self, "")
        hori_layout.add(self.created_label, expand=True)
        hori_layout.add_spacer(20)
        self.abort_button = fsui.Button(self, gettext("Stop"))
        self.abort_button.activated.connect(self.on_abort_activated)
        hori_layout.add(self.abort_button)

        self.set_size(self.layout.get_min_size())
        self.center_on_parent()

        self.task = task
        self.task.progressed.connect(self.on_progress)
        self.task.failed.connect(self.on_failure)
        self.task.succeeded.connect(self.close)
        self.task.stopped.connect(self.close)
        self.task.start()

    def __del__(self):
        print("TaskDialog.__del__")

    def on_close(self):
        self.task.stop()

    def on_abort_activated(self):
        self.task.stop()
        self.abort_button.disable()

    def on_failure(self, message):
        fsui.show_error(message, parent=self.get_window())

    def on_progress(self, message):
        if not isinstance(message, str):
            message = message[0]
        # print("on_progress", status)
        self.icon_header.subtitle_label.set_text(message)
