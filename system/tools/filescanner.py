from typing import List, Optional

import fsui
from fsgamesys.amiga.amiga import Amiga
from fsgamesys.context import fsgs
from fsgamesys.product import Product
from fsui import Button
from fsui.common.layout import Layout
from fswidgets.panel import Panel
from fswidgets.widget import Widget
from launcher.i18n import gettext
from launcher.launcher_signal import LauncherSignal
from launcher.scanner import Scanner
from launcher.settings.scan_paths_group import ScanPathsGroup
from system.classes.window import Window

TIMER_INTERVAL = 100


# FIXM: TODO: When clicking the Stop button, old (existing) data may be purged


class FileScannerWindow(Window):
    @classmethod
    def refresh_game_database(cls, window: Widget) -> "FileScannerWindow":
        return cls(
            window, minimal=True, interactive=False, scan_for_files=False
        )

    def __init__(
        self,
        parent: Optional[Widget] = None,
        minimal: bool = False,
        interactive: bool = True,
        scan_for_files: bool = True,
    ) -> None:
        title = gettext("File scanner")
        super().__init__(parent, title=title, maximizable=False)

        buttons, layout = fsui.DialogButtons.create_with_layout(
            self, create_parent_layout=False
        )
        buttons.create_close_button()

        self.layout.add_spacer(640, 0)

        self.interactive = interactive
        self.scan_for_files = scan_for_files
        self.update_game_database = False

        if not minimal:
            if Product.includes_amiga():
                self.scan_kickstart_group = ScanKickstartGroup(self)
                layout.add(self.scan_kickstart_group, fill=True)
                layout.add_spacer(20)
                heading = gettext(
                    "Scan for Kickstarts, Files and Configurations"
                )
            else:
                heading = gettext("Scan for ROMs, media and config files")
            label = fsui.HeadingLabel(self, heading)
            layout.add(label, margin_bottom=10)

            self.scan_paths_group = ScanPathsGroup(self)
            layout.add(self.scan_paths_group, fill=True, margin=0)

            layout.add_spacer(20)

        self.scan_progress_group = ScanProgressGroup(self)
        layout.add(self.scan_progress_group, fill=True)

        self.scan_button: Optional[Button]
        if interactive:
            self.scan_button = buttons.add_button(
                fsui.Button(buttons, gettext("Scan"))
            )
            self.scan_button.activated.connect(self.on_scan_button)
        else:
            self.scan_button = None

        self.stop_button = buttons.add_button(
            fsui.Button(buttons, gettext("Stop"))
        )
        self.stop_button.activated.connect(self.on_stop_button)

        self.old_title = ""
        self.old_status = ""
        self.has_started_scan = False

        self.start_timer(TIMER_INTERVAL)

        if not self.interactive:
            self.start_scan()

        self.destroyed.connect(Scanner.stop)

    def set_scan_title(self, text: str) -> None:
        if not text:
            return
        if text == self.old_title:
            return
        self.old_title = text
        self.scan_progress_group.title_label.set_text(text)

    def set_scan_status(self, text: str) -> None:
        if not text:
            return
        if text == self.old_status:
            return
        self.old_status = text
        self.scan_progress_group.status_label.set_text(text)

    def on_timer(self) -> None:
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
                        gettext("Click 'Scan' button if you want to re-scan")
                    )
            else:
                self.set_scan_title(gettext("No scan in progress"))
                self.set_scan_status(
                    gettext("Click 'Scan' button to start scan")
                )
            if self.scan_button is not None:
                self.scan_button.set_enabled()
            self.stop_button.set_enabled(False)
            return

        status = Scanner.status
        self.set_scan_title(status[0])
        self.set_scan_status(status[1])

    def on_scan_button(self) -> None:
        self.start_scan()

    def start_scan(self) -> None:
        if self.scan_button is not None:
            self.scan_button.set_enabled(False)
        self.has_started_scan = True
        self.set_scan_title(gettext("Starting scan"))
        self.set_scan_status(gettext("Please wait..."))
        paths = ScanPathsGroup.get_search_path()

        self.stop_button.set_enabled()

        Scanner.start(
            paths,
            scan_for_files=self.scan_for_files,
            update_game_database=self.update_game_database,
            purge_other_dirs=True,
        )

    # noinspection PyMethodMayBeStatic
    def on_stop_button(self) -> None:
        Scanner.stop_flag = True


class KickstartStatusGroup(fsui.Panel):
    def __init__(self, parent: Widget, title: str, model: str) -> None:
        self.model = model
        super().__init__(parent)
        self.layout = fsui.HorizontalLayout()

        self.ok_image = fsui.Image("launcher:/data/ok_emblem.png")
        self.na_image = fsui.Image("launcher:/data/na_emblem.png")

        self.icon = fsui.ImageView(self, self.na_image)
        self.layout.add(self.icon)

        self.layout.add_spacer(10)
        self.label = fsui.Label(self, title)
        self.layout.add(self.label)
        self.update()
        LauncherSignal.add_listener("scan_done", self)

    def onDestroy(self) -> None:
        LauncherSignal.remove_listener("scan_done", self)
        super().onDestroy()

    def on_scan_done_signal(self) -> None:
        self.update()

    def update(self) -> None:
        amiga = Amiga.get_model_config(self.model)
        for sha1 in amiga["kickstarts"]:
            if fsgs.file.find_by_sha1(sha1):
                self.icon.set_image(self.ok_image)
                return
        self.icon.set_image(self.na_image)


class ScanKickstartGroup(Panel):
    def __init__(self, parent: Widget) -> None:
        super().__init__(parent)

        self.layout = fsui.VerticalLayout()
        headingLabel = fsui.HeadingLabel(
            self, gettext("Available Kickstart Versions")
        )
        self.layout.add(headingLabel, margin_bottom=10)

        icon_layout = fsui.HorizontalLayout()
        self.layout.add(icon_layout, fill=True)

        icon_layout.add_spacer(20)
        image = fsui.Image("launcher:/data/kickstart.png")
        self.image_view = fsui.ImageView(self, image)
        icon_layout.add(self.image_view, valign=0.0, margin_right=10)

        vert_layout = fsui.VerticalLayout()
        icon_layout.add(vert_layout, fill=True, expand=True)

        vert_layout.add_spacer(0)

        label = fsui.Label(
            self,
            gettext(
                "You should have kickstart files for "
                "each Amiga model you want to use:"
            ),
        )
        vert_layout.add(label, margin_bottom=0)

        hori_layout = fsui.HorizontalLayout()
        vert_layout.add(hori_layout, fill=True)

        self.kickstart_groups: List[fsui.Panel] = []

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

    def add_kickstart_group(
        self, layout: Layout, title: str, model: str
    ) -> None:
        group = KickstartStatusGroup(self, title, model)
        self.kickstart_groups.append(group)
        layout.add(group, fill=True)


class ScanProgressGroup(Panel):
    def __init__(self, parent: Widget) -> None:
        super().__init__(parent)
        self.layout = fsui.HorizontalLayout()

        self.layout2 = fsui.VerticalLayout()
        self.layout.add(self.layout2, fill=True, expand=True)

        self.title_label = fsui.HeadingLabel(self, "")
        self.layout2.add(self.title_label, fill=True)

        self.layout2.add_spacer(10)
        self.status_label = fsui.Label(self, "")
        self.layout2.add(self.status_label, fill=True)
