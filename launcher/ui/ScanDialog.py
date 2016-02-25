import fsui as fsui
from ..scanner import Scanner
from ..i18n import gettext
from .settings.scan_paths_group import ScanPathsGroup


TIMER_INTERVAL = 100


class ScanDialog(fsui.Window):

    @classmethod
    def refresh_game_database(cls, window):
        return cls(window, minimal=True, interactive=False,
                   scan_for_files=False)

    def __init__(self, parent, minimal=False, interactive=True,
                 scan_for_files=True):
        super().__init__(parent, gettext("Update File Database"))
        buttons, layout = fsui.DialogButtons.create_with_layout(self)
        buttons.create_close_button()

        self.layout.add_spacer(640, 0)

        self.interactive = interactive
        self.scan_for_files = scan_for_files
        self.update_game_database = False
        # self.update_game_database = True

        if not minimal:
            # layout.add_spacer(20)

            from .ScanKickstartGroup import ScanKickstartGroup
            self.scan_kickstart_group = ScanKickstartGroup(self)
            layout.add(self.scan_kickstart_group, fill=True)

            layout.add_spacer(20)

            label = fsui.HeadingLabel(
                self, gettext("Scan for Kickstarts, Files and Configurations"))
            layout.add(label, margin_bottom=10)

            self.scan_paths_group = ScanPathsGroup(self)
            layout.add(self.scan_paths_group, fill=True, margin=0)

            layout.add_spacer(20)

        from .ScanProgressGroup import ScanProgressGroup
        self.scan_progress_group = ScanProgressGroup(self)
        layout.add(self.scan_progress_group, fill=True)

        # layout.add_spacer(20)
        # layout.add_spacer(20)

        # hor_layout = fsui.HorizontalLayout()
        # layout.add(hor_layout, fill=True)

        # hor_layout.add_spacer(10, expand=True)
        if interactive:
            self.scan_button = buttons.add_button(
                fsui.Button(buttons, gettext("Scan")))
            # self.scan_button = fsui.Button(self, _("Scan"))
            # hor_layout.add(self.scan_button)
            # hor_layout.add_spacer(10)
            self.scan_button.activated.connect(self.on_scan_button)
        else:
            self.scan_button = None

        # self.stop_button = fsui.Button(self, _("Abort"))
        # hor_layout.add(self.stop_button)
        self.stop_button = buttons.add_button(
            fsui.Button(buttons, gettext("Abort")))
        self.stop_button.activated.connect(self.on_stop_button)

        # hor_layout.add_spacer(10)
        # self.close_button = fsui.Button(self, _("Close"))
        # self.close_button.activated.connect(self.on_close_button
        # hor_layout.add(self.close_button)
        # hor_layout.add_spacer(10)

        # layout.add_spacer(10)

        # self.set_size(layout.get_min_size())
        # self.center_on_parent()

        self.old_title = ""
        self.old_status = ""
        self.has_started_scan = False

        self.timer = fsui.IntervalTimer(TIMER_INTERVAL)
        self.timer.activated.connect(self.on_timer)
        self.closed.connect(self.timer.stop)

        if not self.interactive:
            self.start_scan()

    def on_close(self):
        Scanner.stop_flag = True

    def on_destroy(self):
        Scanner.stop_flag = True

    def set_scan_title(self, text):
        if not text:
            return
        if text == self.old_title:
            return
        self.old_title = text
        self.scan_progress_group.title_label.set_text(text)

    def set_scan_status(self, text):
        if not text:
            return
        if text == self.old_status:
            return
        self.old_status = text
        self.scan_progress_group.status_label.set_text(text)

    def on_timer(self):
        if not Scanner.running:
            if self.has_started_scan:
                if Scanner.error:
                    self.set_scan_title(gettext("Scan error"))
                    self.set_scan_status(Scanner.error)
                else:
                    if not self.interactive:
                        self.end_modal(True)
                        return
                    self.set_scan_title(gettext("Scan complete"))
                    self.set_scan_status(
                        gettext("Click 'Scan' button if you want to re-scan"))
            else:
                self.set_scan_title(gettext("No scan in progress"))
                self.set_scan_status(
                    gettext("Click 'Scan' button to start scan"))
            if self.scan_button is not None:
                self.scan_button.enable()
            self.stop_button.disable()
            # self.close_button.enable()
            return

        status = Scanner.status
        self.set_scan_title(status[0])
        self.set_scan_status(status[1])

    def on_scan_button(self):
        self.start_scan()

    def start_scan(self):
        if self.scan_button is not None:
            self.scan_button.disable()
        self.has_started_scan = True
        self.set_scan_title(gettext("Starting scan"))
        self.set_scan_status(gettext("Please wait..."))
        paths = ScanPathsGroup.get_search_path()

        # self.close_button.disable()
        self.stop_button.enable()

        Scanner.start(paths, scan_for_files=self.scan_for_files,
                      update_game_database=self.update_game_database,
                      purge_other_dirs=True)

    # def on_close_button(self):
    #     self.end_modal(False)

    def on_stop_button(self):
        Scanner.stop_flag = True
        # self.close_button.enable()
