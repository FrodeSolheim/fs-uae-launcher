import fsui as fsui
from ..I18N import gettext


class LaunchDialog(fsui.LegacyDialog):

    def __init__(self, parent, title, task):
        fsui.LegacyDialog.__init__(self, parent, title)
        self.layout = fsui.VerticalLayout()

        self.layout.add_spacer(400, 20)

        hor_layout = fsui.HorizontalLayout()
        self.layout.add(hor_layout, fill=True)

        hor_layout.padding_right = 20
        hor_layout.add_spacer(20)

        image = fsui.Image("fs_uae_launcher:res/fs_uae_group.png")
        self.image_view = fsui.ImageView(self, image)
        hor_layout.add(self.image_view, valign=0.0)
        hor_layout.add_spacer(20)

        ver_layout = fsui.VerticalLayout()
        hor_layout.add(ver_layout, fill=True, expand=True)
        self.title_label = fsui.HeadingLabel(self, title)
        ver_layout.add(self.title_label, fill=True)

        ver_layout.add_spacer(6)
        self.sub_title_label = fsui.Label(self, gettext("Preparing..."))
        ver_layout.add(self.sub_title_label, fill=True)

        self.layout.add_spacer(20)

        hor_layout = fsui.HorizontalLayout()
        self.layout.add(hor_layout, fill=True)

        hor_layout.add_spacer(20, expand=True)
        self.cancel_button = fsui.Button(self, gettext("Cancel"))
        self.cancel_button.activated.connect(self.on_cancel_button)
        hor_layout.add(self.cancel_button)
        hor_layout.add_spacer(20)

        self.layout.add_spacer(20)
        self.set_size(self.layout.get_min_size())
        self.center_on_parent()

        self.was_closed = False
        self.task = task
        self.task.progressed.connect(self.on_progress)
        self.task.finished.connect(self.on_complete)
        self.task.failed.connect(self.on_error)

    def complete(self):
        self.was_closed = True
        self.end_modal(0)

    def on_close(self):
        self.cancel()
        return False

    def on_progress(self, progress):
        def function():
            self.sub_title_label.set_text(progress)
        fsui.call_after(function)

    def on_complete(self):
        def function():
            self.complete()
        fsui.call_after(function)

    def on_error(self, message):
        self.end_modal(1)
        fsui.show_error(message)

    def on_cancel_button(self):
        self.cancel()
        # self.handler.on_progress = None
        # self.handler.on_complete = None
        # self.complete()

    def cancel(self):
        print("FIXME: LaunchDialog.cancel")
        self.task.stop()
        self.cancel_button.disable()

    # def handler_thread(self):
    #     try:
    #         self._handler_thread()
    #     except Exception:
    #         traceback.print_exc()
    #         message = traceback.format_exc()
    #
    #         def function():
    #             self.on_error(message)
    #
    #         fsui.call_after(function)
    #
    # def _handler_thread(self):
    #     self.handler.run_sequence()
