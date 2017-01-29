import fsui
from fsgs.amiga.Amiga import Amiga
from fsgs.context import fsgs
from launcher.i18n import gettext
from launcher.launcher_signal import LauncherSignal
from launcher.scanner import Scanner
from launcher.ui.settings.scan_paths_group import ScanPathsGroup
from launcher.ui.widgets import CloseButton

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
            self.scan_kickstart_group = ScanKickstartGroup(self)
            layout.add(self.scan_kickstart_group, fill=True)

            layout.add_spacer(20)

            label = fsui.HeadingLabel(
                self, gettext("Scan for Kickstarts, Files and Configurations"))
            layout.add(label, margin_bottom=10)

            self.scan_paths_group = ScanPathsGroup(self)
            layout.add(self.scan_paths_group, fill=True, margin=0)

            layout.add_spacer(20)

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
            fsui.Button(buttons, gettext("Stop")))
        self.stop_button.activated.connect(self.on_stop_button)

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

    # noinspection PyMethodMayBeStatic
    def on_stop_button(self):
        Scanner.stop_flag = True
        # self.close_button.enable()


class KickstartStatusGroup(fsui.Group):
    def __init__(self, parent, title, model):
        self.model = model
        fsui.Group.__init__(self, parent)
        self.layout = fsui.HorizontalLayout()

        self.ok_image = fsui.Image("launcher:res/ok_emblem.png")
        self.na_image = fsui.Image("launcher:res/na_emblem.png")

        self.icon = fsui.ImageView(self, self.na_image)
        self.layout.add(self.icon)

        self.layout.add_spacer(10)
        self.label = fsui.Label(self, title)
        self.layout.add(self.label)
        self.update()
        LauncherSignal.add_listener("scan_done", self)

    def on_destroy(self):
        LauncherSignal.remove_listener("scan_done", self)

    def on_scan_done_signal(self):
        self.update()

    def update(self):
        amiga = Amiga.get_model_config(self.model)
        for sha1 in amiga["kickstarts"]:
            if fsgs.file.find_by_sha1(sha1):
                self.icon.set_image(self.ok_image)
                return
        self.icon.set_image(self.na_image)


class ScanKickstartGroup(fsui.Group):
    def __init__(self, parent):
        fsui.Group.__init__(self, parent)

        self.layout = fsui.VerticalLayout()
        label = fsui.HeadingLabel(
            self, gettext("Available Kickstart Versions"))
        self.layout.add(label, margin_bottom=10)

        icon_layout = fsui.HorizontalLayout()
        self.layout.add(icon_layout, fill=True)

        icon_layout.add_spacer(20)
        image = fsui.Image("launcher:res/kickstart.png")
        self.image_view = fsui.ImageView(self, image)
        icon_layout.add(self.image_view, valign=0.0, margin_right=10)

        vert_layout = fsui.VerticalLayout()
        icon_layout.add(vert_layout, fill=True, expand=True)

        vert_layout.add_spacer(0)

        label = fsui.Label(
            self, gettext("You should have kickstart files for "
                          "each Amiga model you want to use:"))
        vert_layout.add(label, margin_bottom=0)

        hori_layout = fsui.HorizontalLayout()
        vert_layout.add(hori_layout, fill=True)

        self.kickstart_groups = []

        column_layout = fsui.VerticalLayout()
        hori_layout.add(column_layout, expand=True, fill=True, margin=10)

        self.add_kickstart_group(column_layout, "Amiga 1000", "A1000")
        column_layout.add_spacer(10)
        self.add_kickstart_group(column_layout, "Amiga 500", "A500")
        column_layout.add_spacer(10)
        self.add_kickstart_group(column_layout, "Amiga 500+", "A500+")

        column_layout = fsui.VerticalLayout()
        hori_layout.add(column_layout, expand=True, fill=True, margin=10)

        self.add_kickstart_group(column_layout, "Amiga 600", "A600")
        column_layout.add_spacer(10)
        self.add_kickstart_group(column_layout, "Amiga 1200", "A1200")
        column_layout.add_spacer(10)
        self.add_kickstart_group(column_layout, "Amiga 3000", "A3000")

        column_layout = fsui.VerticalLayout()
        hori_layout.add(column_layout, expand=True, fill=True, margin=10)

        self.add_kickstart_group(column_layout, "Amiga 4000", "A4000/040")
        column_layout.add_spacer(10)
        self.add_kickstart_group(column_layout, "Amiga CD32", "CD32")
        column_layout.add_spacer(10)
        self.add_kickstart_group(column_layout, "Commodore CDTV", "CDTV")

    def add_kickstart_group(self, layout, title, model):
        group = KickstartStatusGroup(self, title, model)
        self.kickstart_groups.append(group)
        layout.add(group, fill=True)


class ScanProgressGroup(fsui.Group):
    def __init__(self, parent):
        fsui.Group.__init__(self, parent)
        self.layout = fsui.HorizontalLayout()
        # self.layout.padding_left = 10
        # self.layout.padding_top = 10
        # self.layout.padding_right = 10
        # self.layout.padding_bottom = 10

        # #image = fsui.Image("launcher:res/search_group.png")
        # #self.image_view = fsui.ImageView(self, image)
        # self.layout.add_spacer(20)
        # #self.layout.add(self.image_view, valign=0.0)
        # self.layout.add_spacer(48)
        # self.layout.add_spacer(20)

        self.layout2 = fsui.VerticalLayout()
        self.layout.add(self.layout2, fill=True, expand=True)

        self.title_label = fsui.HeadingLabel(self, "")
        self.layout2.add(self.title_label, fill=True)

        # self.layout2.add_spacer(10)
        # hor_layout = fsui.HorizontalLayout()
        # self.layout2.add(hor_layout)

        # self.scan_label = fsui.Label(self, _("Scan for:"))
        # hor_layout.add(self.scan_label)
        # hor_layout.add_spacer(10)

        # self.scan_roms = fsui.CheckBox(self, _("ROMs"))
        # if Settings.get("scan_roms") == "1":
        #     self.scan_roms.check()
        # self.scan_roms.on_changed = self.on_change
        # hor_layout.add(self.scan_roms)
        # hor_layout.add_spacer(10)

        # self.scan_files = fsui.CheckBox(self, _("Game Files"))
        # if Settings.get("scan_files") == "1":
        #     self.scan_files.check()
        # self.scan_files.on_changed = self.on_change
        # hor_layout.add(self.scan_files)
        # hor_layout.add_spacer(10)

        # self.scan_configs = fsui.CheckBox(self, _("Configurations"))
        # if Settings.get("scan_configs") == "1":
        #     self.scan_configs.check()
        # self.scan_configs.on_changed = self.on_change
        # hor_layout.add(self.scan_configs)
        # hor_layout.add_spacer(10)

        self.layout2.add_spacer(10)
        self.status_label = fsui.Label(self, "")
        self.layout2.add(self.status_label, fill=True)

        # def on_change(self):
        #     value = "1" if self.scan_roms.is_checked() else "0"
        #     Settings.set("scan_roms", value)
        #     value = "1" if self.scan_files.is_checked() else "0"
        #     Settings.set("scan_files", value)
        #     value = "1" if self.scan_configs.is_checked() else "0"
        #     Settings.set("scan_configs", value)
