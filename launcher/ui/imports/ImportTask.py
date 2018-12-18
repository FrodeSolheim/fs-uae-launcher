import os
import shutil
import threading
import traceback
from fsbc.path import is_same_file
import fsui
from ...i18n import gettext
from fsgs.amiga.rommanager import ROMManager
from fsgs.FSGSDirectories import FSGSDirectories
from ...launcher_signal import LauncherSignal
from fsgs.filedatabase import FileDatabase


class ImportTask(threading.Thread):

    AMIGA_FOREVER = 1

    def __init__(self, path, import_type):
        threading.Thread.__init__(self, name="ImportTaskThread")
        self.path = path
        self.type = import_type
        self.done = False
        self.log_lines = []
        self.log_lock = threading.Lock()

    def run(self):
        if self.type:
            self.log(gettext("Amiga Forever import task started"))
        else:
            self.log(gettext("Kickstart import task started"))
        self.log("")
        print("ImportTask.run")
        try:
            count = self.run_task()
        except Exception as e:
            self.log("")
            self.log(repr(e))
            traceback.print_exc()
        else:
            if count == 0:
                self.log(gettext("Warning: No ROM files were found!"))
            else:
                self.log("")
                self.log(gettext("{} ROM files were imported").format(count))
        self.done = True
        print("ImportTask.run is done")
        self.log("")
        self.log(gettext("Import task is done"))

        def run_in_main():
            LauncherSignal.broadcast("scan_done")

        fsui.call_after(run_in_main)

    def get_new_log_lines(self, count):
        with self.log_lock:
            if len(self.log_lines) <= count:
                return []
            return self.log_lines[count:]

    def log(self, line):
        with self.log_lock:
            self.log_lines.append(line)

    def run_task(self):
        if self.type == 0:
            return self.import_roms()
        elif self.type == 1:
            return self.import_amiga_forever()

    def import_roms(self):
        return self.copy_roms(self.path, FSGSDirectories.get_kickstarts_dir())

    def import_amiga_forever(self):
        return self.copy_roms(os.path.join(
            self.path, "Amiga Files", "Shared", "rom"),
            FSGSDirectories.get_kickstarts_dir())

    def copy_file(self, src, dst):
        with self.log_lock:
            self.log_lines.append(gettext("Copy {0}\nto {1}").format(src, dst))
        if is_same_file(src, dst):
            self.log_lines.append(
                "- source and destination are the same, skipping...")
            return
        if not os.path.exists(os.path.dirname(dst)):
            os.makedirs(os.path.dirname(dst))
        if os.path.exists(dst):
            # try to remove the file first, in case the file has read-only
            # permissions
            try:
                os.remove(dst)
            except Exception:
                pass
        shutil.copy(src, dst)

    def copy_roms(self, src, dst):
        count = 0
        if not os.path.isdir(src):
            self.log("{0} is not a directory".format(src))
            return count
        src_file = os.path.join(src, "rom.key")
        if os.path.exists(src_file):
            dst_file = os.path.join(dst, "rom.key")
            self.copy_file(src_file, dst_file)
        for file_name in os.listdir(src):
            name, ext = os.path.splitext(file_name)
            if ext not in [".rom"]:
                continue
            src_file = os.path.join(src, file_name)
            dst_file = os.path.join(dst, file_name)
            self.copy_file(src_file, dst_file)

            database = FileDatabase.get_instance()
            ROMManager.add_rom_to_database(dst_file, database, self.log)
            database.commit()
            count += 1
        return count
