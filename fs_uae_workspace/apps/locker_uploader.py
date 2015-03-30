import time
import traceback
from fsgs.context import fsgs
from fsgs.Archive import Archive
from fsgs.amiga.ROMManager import ROMManager
import fsui
from fsbc.task import Task
from fsgs.FileDatabase import FileDatabase
from fsgs.ogd.client import OGDClient
from fsui.extra.iconheader import IconHeader
from fs_uae_workspace.shell import SimpleApplication
from fs_uae_launcher.res import gettext
from io import BytesIO as StringIO


class LockerUploaderWindow(fsui.Dialog):

    def __init__(self):
        super().__init__(None, gettext("OAGD.net Locker Uploader"))
        self.set_icon(fsui.Icon("refresh", "pkg:fs_uae_workspace"))

        self.layout = fsui.VerticalLayout()
        self.layout.min_width = 500
        self.layout.set_padding(20, 20, 20, 20)

        self.icon_header = IconHeader(
            self, fsui.Icon("refresh", "pkg:fs_uae_workspace"),
            gettext("OAGD.net Locker Uploader"),
            gettext("Upload recognized Amiga files to your OAGD.net locker"))
        self.layout.add(self.icon_header, fill=True, margin_bottom=20)

        hori_layout = fsui.HorizontalLayout()
        self.layout.add(hori_layout, fill=True)
        self.created_label = fsui.Label(self, "")
        hori_layout.add(self.created_label, expand=True)

        self.stop_button = fsui.Button(self, gettext("Stop"))
        self.stop_button.activated.connect(self.on_stop_activated)
        self.stop_button.disable()
        hori_layout.add(self.stop_button, margin_left=10)

        self.upload_button = fsui.Button(self, gettext("Upload"))
        self.upload_button.activated.connect(self.on_upload_activated)
        hori_layout.add(self.upload_button, margin_left=10)

        self.set_size(self.layout.get_min_size())
        self.center_on_parent()
        self.task = None

    def __del__(self):
        print("LockerUploaderWindow.__del__")

    def on_close(self):
        if self.task is not None:
            self.task.stop()

    def on_upload_activated(self):
        self.upload_button.disable()
        self.stop_button.enable()
        self.task = LockerUploaderTask()
        self.task.progressed.connect(self.on_progress)
        self.task.failed.connect(self.on_failure)
        self.task.succeeded.connect(self.on_success)
        self.task.stopped.connect(self.on_stopped)
        self.task.start()

    def on_stop_activated(self):
        self.task.stop()
        self.stop_button.disable()

    def on_stopped(self):
        self.icon_header.subtitle_label.set_text(gettext("Stopped by user"))
        self.after_task_has_stopped()

    def on_success(self):
        self.after_task_has_stopped()

    def on_failure(self, message):
        fsui.show_error(message, parent=self.get_window())
        self.after_task_has_stopped()

    def after_task_has_stopped(self):
        self.upload_button.enable()
        self.stop_button.disable()

    def on_progress(self, message):
        if not isinstance(message, str):
            message = message[0]
        # print("on_progress", status)
        self.icon_header.subtitle_label.set_text(message)


class LockerUploaderTask(Task):

    def __init__(self):
        Task.__init__(self, "Locker Uploader Task")
        self.client = OGDClient()

    def run(self):
        for i in range(16):
            self.upload_prefix(i)
        self.progressed(gettext("OAGD.net upload task completed successfully"))

    def upload_prefix(self, prefix):
        self.stop_check()
        result = self.upload_check(prefix)
        print(len(result))
        for k in range(0, len(result), 20):
            sha1 = result[k:k + 20]
            path = fsgs.file.find_by_sha1(sha1.encode("hex"))
            if not path:
                continue
            try:
                # this is done to properly handle encrypted ROMs
                archive = Archive(path)
                data = ROMManager.decrypt_archive_rom(archive, path)["data"]
            except Exception:
                traceback.print_exc()
                uri = "sha1://{0}".format(sha1.encode("hex"))
                print(uri)
                try:
                    input_stream = fsgs.file.open(uri)
                    data = input_stream.read()
                except Exception:
                    continue
                assert not input_stream.read()

            print("uploading file of size ", len(data))
            import hashlib
            print(hashlib.sha1(data).hexdigest())
            if hashlib.sha1(data).hexdigest() != sha1.encode("hex"):
                print("hash mismatch, probably Cloanto ROM...")
                continue
            self.progressed(gettext("Uploading {name}").format(
                            name=sha1.encode("hex")))

            retry_seconds = 1
            while True:
                try:
                    self.client.post("/api/locker-upload-file", data=data)
                except OGDClient.NonRetryableHTTPError as e:
                    raise e
                except Exception:
                    self.progressed(gettext(
                        "Re-trying in {0} seconds...").format(retry_seconds))
                    for _ in range(retry_seconds):
                        self.stop_check()
                        time.sleep(1.0)
                    retry_seconds = min(retry_seconds * 2, 60 * 10)
                else:
                    break

    def upload_check(self, prefix):
        self.progressed(
            gettext("Finding files eligible for OAGD.net Locker") +
            " ({0:0.0f}%)".format((100.0 * prefix / 16.0)))
        file_database = FileDatabase.instance()
        cursor = file_database.cursor()
        # FIXME: prefix
        p = "0123456789ABCDEF"[prefix]
        cursor.execute("SELECT DISTINCT sha1 FROM file "
                       "WHERE hex(sha1) LIKE ?", (p + "%",))
        string_io = StringIO()
        for row in cursor:
            string_io.write(row[0])
        # print(prefix, len(string_io.getvalue()))
        self.stop_check()

        retry_seconds = 1
        while True:
            try:
                result = self.client.post("/api/locker-upload-check",
                                          data=string_io.getvalue())
            except OGDClient.ForbiddenError:
                raise Task.Failure(
                    gettext("OAGD.net Locker is not enabled for your user. "
                            "It may be available only to a few select beta "
                            "users."))
            except OGDClient.NonRetryableHTTPError as e:
                raise e
            except Exception:
                self.progressed(gettext(
                    "Re-trying in {0} seconds...").format(retry_seconds))
                for _ in range(retry_seconds):
                    self.stop_check()
                    time.sleep(1.0)
                retry_seconds = min(retry_seconds * 2, 60 * 10)
            else:
                return result

        # try:
        #     result = self.client.post("/api/locker-upload-check",
        #                               data=string_io.getvalue())
        # except OGDClient.ForbiddenError:
        #     raise Task.Failure(
        #         gettext("OAGD.net Locker is not enabled for your user. "
        #                 "It may be available only to a few select beta "
        #                 "users."))
        # string_io.close()
        # return result


application = SimpleApplication(LockerUploaderWindow)
