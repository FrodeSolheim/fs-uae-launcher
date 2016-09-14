import os
import hashlib
import traceback

from fsbc.paths import Paths

from fsgs.FileDatabase import FileDatabase
from fsgs.Archive import Archive
from fsgs.amiga.ROMManager import ROMManager
from fsgs.ogd.client import OGDClient
from .i18n import gettext


class FileScanner(object):

    def __init__(self, paths, purge_other_dirs,
                 on_status=None, on_rom_found=None, stop_check=None):
        self.paths = paths

        self.purge_other_dirs = purge_other_dirs
        self.database_file_ids = []

        self.on_status = on_status
        self.on_rom_found = on_rom_found
        self._stop_check = stop_check
        self.scan_count = 0
        self.files_added = 0
        self.bytes_added = 0

        self.extensions = set()
        self.extensions.add(".rom")
        self.extensions.add(".adf")
        self.extensions.add(".adz")
        self.extensions.add(".ipf")
        self.extensions.add(".dms")
        self.extensions.add(".bin")
        self.extensions.add(".cue")
        self.extensions.add(".iso")
        self.extensions.add(".wav")
        self.extensions.add(".zip")
        self.extensions.add(".lha")
        self.extensions.add(".rp9")
        self.extensions.add(".fs-uae")
        self.extensions.add(".7z")

        # if OGDClient.get_server() != "oagd.net":
        if True:
            self.extensions.add(".bin")

            # Amstrad CPC
            self.extensions.add(".dsk")

            # Atari 2600
            self.extensions.add(".a26")

            # Atari 5200
            self.extensions.add(".a52")

            # Atari 7800
            self.extensions.add(".a78")

            # Atari ST
            self.extensions.add(".st")  # disk images
            self.extensions.add(".img")  # bios images
            self.extensions.add(".bin")  # bios images

            # Game Boy
            self.extensions.add(".gb")

            # Game Boy Advance
            self.extensions.add(".gba")

            # Game Boy Color
            self.extensions.add(".gbc")

            # Master System
            self.extensions.add(".sms")

            # Mega Drive
            self.extensions.add(".md")
            self.extensions.add(".bin")
            self.extensions.add(".gen")

            # Nintendo
            self.extensions.add(".nes")

            # Super Nintendo
            self.extensions.add(".sfc")

            # ZX Spectrum
            self.extensions.add(".dsk")
            self.extensions.add(".tap")
            self.extensions.add(".tzx")
            self.extensions.add(".z80")

    def stop_check(self):
        if self._stop_check:
            return self._stop_check()

    def set_status(self, title, status):
        if self.on_status:
            self.on_status((title, status))

    def get_scan_dirs(self):
        return self.paths

    def purge_file_ids(self, file_ids):
        self.set_status(gettext("Scanning files"),
                        gettext("Purging old entries..."))
        database = FileDatabase.get_instance()
        for file_id in file_ids:
            database.delete_file(id=file_id)

    def scan(self):
        self.set_status(gettext("Scanning files"),
                        gettext("Scanning files"))
        database = FileDatabase.get_instance()
        # database.clear()
        scan_dirs = self.get_scan_dirs()
        
        if self.purge_other_dirs:
            all_database_file_ids = database.get_file_ids()
        else:
            all_database_file_ids = None

        for dir in scan_dirs:
            if not os.path.exists(dir):
                print("[SCANNER] Directory does not exist:", dir)
                continue
            # this is important to make sure the database is portable across
            # operating systems
            dir = Paths.get_real_case(dir)

            self.database_file_ids = database.get_file_hierarchy_ids(dir)
            if self.purge_other_dirs:
                all_database_file_ids.difference_update(
                    self.database_file_ids)

            self.scan_dir(database, dir)

            # print("Remaining files:", self.database_file_ids)
            self.purge_file_ids(self.database_file_ids)

            self.set_status(gettext("Scanning files"),
                            gettext("Committing data..."))
            # update last_file_insert and last_file_delete
            database.update_last_event_stamps()
            print("FileScanner.scan - committing data")
            database.commit()

        if self.purge_other_dirs:
            self.purge_file_ids(all_database_file_ids)

        if self.stop_check():
            database.rollback()
        else:
            self.set_status(gettext("Scanning files"),
                            gettext("Committing data..."))
            print("FileScanner.scan - committing data")
            database.commit()

    def scan_dir(self, database, dir, all_files=False):
        if not os.path.exists(dir):
            return
        dir_content = os.listdir(dir)
        if not all_files:
            for name in dir_content:
                if not check_valid_name(name):
                    continue
                l_name = name.lower()
                if l_name.endswith(".slave") or l_name.endswith(".slave"):
                    all_files = True
                    break

        for name in dir_content:
            if not check_valid_name(name):
                continue
            if self.stop_check():
                return
            if name in [".git", "Cache", "Save States"]:
                continue

            path = os.path.join(dir, name)
            if os.path.isdir(path):
                self.scan_dir(database, path, all_files=all_files)
                continue
            if not all_files:
                dummy, ext = os.path.splitext(path)
                ext = ext.lower()
                if ext not in self.extensions:
                    continue
            try:
                self.scan_file(database, path)
            except Exception:
                traceback.print_exc()

    def scan_file(self, database, path):
        name = os.path.basename(path)
        # path = os.path.normcase(os.path.normpath(path))

        self.scan_count += 1
        self.set_status(
            gettext("Scanning files ({count} scanned)").format(
                count=self.scan_count), name)

        try:
            st = os.stat(path)
        except:
            print("error stat-ing file", repr(path))
            return
        size = st.st_size
        mtime = int(st.st_mtime)

        result = database.find_file(path=path)
        # print(result)
        if result["path"]:
            if size == result["size"] and mtime == result["mtime"]:

                self.database_file_ids.remove(result["id"])
                # self.database_file_ids.difference_update(
                #         database.get_file_hierarchy_ids(path + "#"))
                
                # self.database_file_ids.difference_update(
                #         database.get_child_ids(id=result["id"]))
                return

        archive = Archive(path)
        # if archive.is_archive():

        file_id = self.scan_archive_stream(
            database, archive, path, name, size, mtime)

        for p in archive.list_files():
            if p.endswith("/"):
                # don't index archive directory entries
                continue
            # print(p)
            if self.stop_check():
                return
            # n = p.replace("\\", "/").replace("|", "/").split("/")[-1]
            n = os.path.basename(p)
            self.scan_count += 1
            self.scan_archive_stream(
                database, archive, p, n, size, mtime, parent=file_id)
        if self.stop_check():
            return

    def scan_archive_stream(
            self, database, archive, path, name, size, mtime, parent=None):
        self.set_status(
            gettext("Scanning files ({count} scanned)").format(
                count=self.scan_count), name)
        base_name, ext = os.path.splitext(name)
        ext = ext.lower()

        f = archive.open(path)
        s = hashlib.sha1()
        while True:
            if self.stop_check():
                return
            data = f.read(65536)
            if not data:
                break
            s.update(data)
        sha1 = s.hexdigest()

        if ext == ".rom":
            try:
                sha1_dec = ROMManager.decrypt_archive_rom(archive, path)["sha1"]
            except Exception:
                import traceback
                traceback.print_exc()
                sha1_dec = None
            if sha1_dec:
                if sha1_dec != sha1:
                    print("found encrypted rom {0} => {1}".format(
                        sha1, sha1_dec))
                    # sha1 is now the decrypted sha1, not the actual sha1 of the
                    # file itself, a bit ugly, since md5 and crc32 are still
                    # encrypted hashes, but it works well with the kickstart
                    # lookup mechanism
                    sha1 = sha1_dec
            else:
                # If the ROM was encrypted and could not be decrypted, we
                # don't add it to the database. This way, the file will be
                # correctly added on later scans if rom.key is added to the
                # directory.
                return None

        if parent:
            path = "#/" + path.rsplit("#/", 1)[1]
        file_id = database.add_file(
            path=path, sha1=sha1, mtime=mtime, size=size, parent=parent)

        self.files_added += 1
        self.bytes_added += size

        if ext == '.rom':
            if self.on_rom_found:
                self.on_rom_found(path, sha1)
        return file_id


def check_valid_name(name):
    # check that the file is actually unicode object (indirectly). listdir
    # will return str objects for file names on Linux with invalid encoding.
    # FIXME: not needed for Python 3
    try:
        str(name)
    except UnicodeDecodeError:
        return False
    return True
