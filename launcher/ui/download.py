from launcher.file_scanner import FileScanner
from fsgs.Downloader import Downloader
from fsgs.FSGSDirectories import FSGSDirectories
import fsui
from fsui.extra.iconheader import IconHeader
import time
from fsbc.application import app
from urllib.request import urlopen
from fsbc.signal import Signal
from fsbc.task import Task
from fsgs.Database import Database
from fsgs.ogd.context import SynchronizerContext
from launcher.game_scanner import GameScanner
from ..i18n import gettext


class DownloadGameWindow(fsui.Window):

    def __init__(self, parent, fsgs):
        fsui.Window.__init__(self, parent, gettext("Download Game Manually"))
        self.fsgs = fsgs
        self.download_page = fsgs.config.get("download_page")
        self.download_notice = fsgs.config.get("download_notice")
        self.task = None

        self.layout = fsui.VerticalLayout()
        self.layout.set_padding(20, 20, 20, 20)

        self.icon_header = IconHeader(
            self, fsui.Icon("web-browser", "pkg:workspace"),
            gettext("Download Game Manually"),
            gettext("This game must be downloaded before you can play it"))
        self.layout.add(self.icon_header, fill=True, margin_bottom=20)

        label = fsui.HeadingLabel(self, gettext(
            "Please open the following web page and download the "
            "game from there:"))
        label.set_min_width(500)
        self.layout.add(label)

        hori_layout = fsui.HorizontalLayout()
        self.layout.add(hori_layout, fill=True, margin_top=10)

        hori_layout.add(fsui.ImageView(self, fsui.Image(
            "launcher:res/16/world_link.png")))

        label = fsui.URLLabel(self, self.download_page, self.download_page)
        hori_layout.add(label, margin_left=6)

        if self.download_notice:
            label = fsui.MultiLineLabel(self, self.download_notice)
            label.set_min_width(500)
            self.layout.add(label, margin_top=20)

        label = fsui.HeadingLabel(self, gettext(
            "Download to the following directory, and then "
            "click '{0}':".format(gettext("Scan Downloads"))))
        label.set_min_width(500)
        self.layout.add(label, margin_top=20)

        hori_layout = fsui.HorizontalLayout()
        self.layout.add(hori_layout, fill=True, margin_top=10)

        hori_layout.add(fsui.ImageView(self, fsui.Image(
            "launcher:res/16/folder.png")))

        label = fsui.Label(self, FSGSDirectories.ensure_downloads_dir())
        hori_layout.add(label, margin_left=6)

        hori_layout = fsui.HorizontalLayout()
        self.layout.add(hori_layout, fill=True, margin_top=20)

        self.status_label = fsui.Label(self, "")
        hori_layout.add(self.status_label, expand=True)

        self.scan_button = fsui.Button(self, gettext("Scan Downloads"))
        self.scan_button.activated.connect(self.on_scan_files)
        hori_layout.add(self.scan_button, margin_left=20)

        self.close_button = fsui.Button(self, gettext("Close"))
        self.close_button.activated.connect(self.on_close)
        hori_layout.add(self.close_button, margin_left=10)

        self.set_size(self.layout.get_min_size())
        self.center_on_parent()

    def on_close(self):
        self.close()

    def on_scan_files(self):
        self.scan_button.disable()

        self.task = RescanTask()
        self.task.progressed.connect(self.on_progress)
        self.task.failed.connect(self.on_failure)
        self.task.succeeded.connect(self.on_success)
        # self.task.stopped.connect(self.close)
        self.task.start()

    def on_progress(self, message):
        if not isinstance(message, str):
            message = message[0]
        # self.icon_header.subtitle_label.set_text(message)
        self.status_label.set_text(message)

    def on_failure(self, message):
        fsui.show_error(message, parent=self.get_window())
        self.scan_button.enable()
        self.status_label.set_text("")

    def on_success(self):
        if self.fsgs.config.get("x_missing_files"):
            message = gettext(
                "Files for this game are still missing. Did you download "
                "the game and put the file(s) in the Downloads directory?")
            fsui.show_error(message, title=gettext("Missing Files"),
                            parent=self.get_window())
            self.scan_button.enable()
            self.status_label.set_text("")
        else:
            self.close()


class RescanTask(Task):

    def __init__(self):
        Task.__init__(self, "RescanTask")

    # def stop_check(self):
    #     pass

    def on_status(self, status):
        self.progressed(status)

    def run(self):
        with Database.get_instance() as database:
            self._run(database)

    def _run(self, database):
        context = SynchronizerContext()

        paths = [FSGSDirectories.downloads_dir()]
        scanner = FileScanner(
            paths, purge_other_dirs=False, on_status=self.on_status,
            stop_check=self.stop_check)
        scanner.scan()

        scanner = GameScanner(
            context, None, on_status=self.on_status,
            stop_check=self.stop_check)
        scanner.scan(database)

        # FIXME: review what signals should be sent when a scan is performed
        # FIXME: these should be removed soon
        app.settings["last_scan"] = str(time.time())
        app.settings["config_refresh"] = str(time.time())
        # this must be called from main, since callbacks are broadcast
        # when settings are changed
        Signal("scan_done").notify()


class DownloadTermsDialog(fsui.LegacyDialog):

    def __init__(self, parent, fsgs):
        fsui.LegacyDialog.__init__(self, parent, gettext("Terms of Download"))
        self.fsgs = fsgs
        self.download_file = fsgs.config.get("download_file")
        self.download_terms = fsgs.config.get("download_terms")
        self.task = None

        self.layout = fsui.VerticalLayout()
        self.layout.set_padding(20, 20, 20, 20)

        self.icon_header = IconHeader(
            self, fsui.Icon("web-browser", "pkg:workspace"),
            gettext("Terms of Download"),
            gettext("This game can be automatically downloaded if you "
                    "accept the terms"))
        self.layout.add(self.icon_header, fill=True, margin_bottom=20)

        self.label = fsui.MultiLineLabel(self, gettext("Loading..."))
        self.label.set_min_width(600)
        self.label.set_min_height(100)
        self.layout.add(self.label)

        hori_layout = fsui.HorizontalLayout()
        self.layout.add(hori_layout, fill=True, margin_top=20)

        hori_layout.add_spacer(0, expand=True)

        self.reject_button = fsui.Button(self, gettext("Reject"))
        self.reject_button.activated.connect(self.on_reject_button)
        hori_layout.add(self.reject_button, margin_left=10)

        self.accept_button = fsui.Button(self, gettext("Accept"))
        self.accept_button.activated.connect(self.on_accept_button)
        hori_layout.add(self.accept_button, margin_left=10)

        self.accept_button.disable()
        self.reject_button.disable()

        self.task = DownloadTermsTask(self.download_terms)
        # self.task.progressed.connect(self.on_progress)
        self.task.failed.connect(self.on_failure)
        self.task.succeeded.connect(self.on_success)
        self.task.start()

        self.set_size(self.layout.get_min_size())
        self.center_on_parent()

    def on_accept_button(self):
        self.end_modal(True)
        Downloader.set_terms_accepted(self.download_file, self.download_terms)

    def on_reject_button(self):
        self.end_modal(False)

    def on_failure(self, message):
        fsui.show_error(message, parent=self.get_window())

    def on_success(self):
        self.label.set_text(self.task.data)
        self.reject_button.enable()
        self.accept_button.enable()
        self.accept_button.focus()


class DownloadTermsTask(Task):

    def __init__(self, url):
        Task.__init__(self, "DownloadTermsTask")
        self.url = url
        self.data = None

    def run(self):
        for i in range(3):
            try:
                self.data = urlopen(self.url).read().decode("UTF-8")
            except Exception:
                time.sleep(0.5)
            else:
                return
        self.data = urlopen(self.url).read().decode("UTF-8")
