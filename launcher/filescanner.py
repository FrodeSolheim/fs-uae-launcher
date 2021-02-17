import hashlib
import os
import traceback

from fsbc.paths import Paths
from fsgamesys.amiga.rommanager import ROMManager
from fsgamesys.archive import Archive, archive_extensions
from fsgamesys.filedatabase import FileDatabase

from .i18n import gettext


class FileScanner(object):
    def __init__(
        self,
        paths,
        purge_other_dirs,
        on_status=None,
        on_rom_found=None,
        stop_check=None,
    ):
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

        # This will add .zip, .rp9 and .lha, .7z (if extensions are present)
        self.extensions.update(archive_extensions)

        self.extensions.add(".rom")
        self.extensions.add(".adf")
        self.extensions.add(".ipf")
        self.extensions.add(".dms")
        self.extensions.add(".bin")
        self.extensions.add(".cue")
        self.extensions.add(".iso")
        self.extensions.add(".wav")
        self.extensions.add(".fs-uae")

        if True:
            self.extensions.add(".fs-fuse")

        if True:
            self.extensions.add(".bin")

            # Amstrad CPC
            self.extensions.add(".dsk")

            # Arcade
            self.extensions.add(".chd")

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

            # Commodore 64
            self.extensions.add(".d64")
            self.extensions.add(".tap")
            self.extensions.add(".t64")

            # DOS / GOG
            # self.extensions.add(".mp3")
            # self.extensions.add(".ogg")

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
            # FIXME: Is .smd a common extension?
            self.extensions.add(".smd")

            # Nintendo
            self.extensions.add(".nes")

            # Nintendo 64
            self.extensions.add(".n64")
            self.extensions.add(".v64")
            self.extensions.add(".z64")

            # Nintendo DS
            self.extensions.add(".nds")

            # Super Nintendo
            self.extensions.add(".sfc")
            self.extensions.add(".smc")

            # TurboGrafx-CD system ROM
            self.extensions.add(".pce")

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
        self.set_status(
            gettext("Scanning files"), gettext("Purging old entries...")
        )
        database = FileDatabase.get_instance()
        for file_id in file_ids:
            database.delete_file(id=file_id)

    def scan(self):
        self.set_status(gettext("Scanning files"), gettext("Scanning files"))
        file_database = FileDatabase.get_instance()
        # database.clear()
        scan_dirs = self.get_scan_dirs()

        if self.purge_other_dirs:
            all_database_file_ids = file_database.get_file_ids()
        else:
            all_database_file_ids = None

        for dir_ in scan_dirs:
            if not os.path.exists(dir_):
                print("[FILES] Scanner: Directory does not exist:", dir_)
                continue
            # this is important to make sure the database is portable across
            # operating systems
            dir_ = Paths.get_real_case(dir_)

            self.database_file_ids = file_database.get_file_hierarchy_ids(dir_)
            if self.purge_other_dirs:
                all_database_file_ids.difference_update(self.database_file_ids)

            self.scan_dir(file_database, dir_)

            print("Remaining files:", self.database_file_ids)
            self.purge_file_ids(self.database_file_ids)

            self.set_status(
                gettext("Scanning files"), gettext("Committing data...")
            )
            # update last_file_insert and last_file_delete
            file_database.update_last_event_stamps()
            print("[FILES] FileScanner.scan - committing data")
            file_database.commit()

        if self.purge_other_dirs:
            self.purge_file_ids(all_database_file_ids)

        if self.stop_check():
            file_database.rollback()
        else:
            self.set_status(
                gettext("Scanning files"), gettext("Committing data...")
            )
            print("[FILES] FileScanner.scan - committing data")
            file_database.commit()

    def scan_dir(self, file_database, dir_, all_files=False):
        if not os.path.exists(dir_):
            return
        dir_content = os.listdir(dir_)
        if not all_files:
            for name in dir_content:
                if not check_valid_name(name):
                    continue
                l_name = name.lower()
                if l_name.endswith(".slave") or l_name.endswith(".slav"):
                    all_files = True
                    break

        for name in sorted(dir_content):
            if not check_valid_name(name):
                continue
            if self.stop_check():
                return
            if name in [".git", "Cache", "Save States"]:
                continue

            path = os.path.join(dir_, name)
            if os.path.isdir(path):
                self.scan_dir(file_database, path, all_files=all_files)
                continue
            if not all_files:
                dummy, ext = os.path.splitext(path)
                ext = ext.lower()
                if ext not in self.extensions:
                    continue
            try:
                self.scan_file(file_database, path)
            except Exception:
                traceback.print_exc()

    def scan_file(self, file_database, path):
        name = os.path.basename(path)
        # path = os.path.normcase(os.path.normpath(path))

        self.scan_count += 1
        self.set_status(
            gettext("Scanning files ({count} scanned)").format(
                count=self.scan_count
            ),
            name,
        )

        try:
            st = os.stat(path)
        except:
            print("[FILES] WARNING: Error stat-ing file", repr(path))
            return
        size = st.st_size
        mtime = int(st.st_mtime)

        result = file_database.find_file(path=path)
        if result["path"]:
            if size == result["size"] and mtime == result["mtime"]:
                # We've already got this file indexed.
                self.database_file_ids.remove(result["id"])
                return

        archive = Archive(path)
        file_id = self.scan_archive_stream(
            file_database, archive, path, name, size, mtime
        )
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
                file_database, archive, p, n, size, mtime, parent=file_id
            )
        if self.stop_check():
            return

    def scan_archive_stream(
        self, database, archive, path, name, size, mtime, parent=None
    ):
        self.set_status(
            gettext("Scanning files ({count} scanned)").format(
                count=self.scan_count
            ),
            name,
        )

        f = None
        sha1 = None
        raw_sha1_obj = hashlib.sha1()
        filter_sha1_obj = hashlib.sha1()
        filter_name = ""
        filter_size = 0

        base_name, ext = os.path.splitext(name)
        ext = ext.lower()
        if ext == ".nes":
            # FIXME: NES header hack. Would be better to add a proper notion of
            # file filters to the file database.
            # FIXME: This will confuse some functionality, such as the
            # Locker uploader or other tools expecting on-disk data to match
            # the database checksum (this also applies to the Cloanto ROM
            # hack). Should be done properly.
            f = archive.open(path)
            data = f.read(16)
            if len(data) == 16 and data.startswith(b"NES\x1a"):
                print("Stripping iNES header for", path)
                filter_name = "Skip(16)"
            raw_sha1_obj.update(data)
        elif ext == ".a78":
            # FIXME: Check if 128 is a fixed or variable number of bytes
            f = archive.open(path)
            data = f.read(128)
            if len(data) == 128 and data[1:10] == b"ATARI7800":
                print("Stripping A78 header for", path)
                filter_name = "Skip(128)"
            raw_sha1_obj.update(data)
        elif ext == ".smc":
            f = archive.open(path)
            data = f.read(512)
            if len(data) == 512 and all(map(lambda x: x == 0, data[48:])):
                print("Stripping SMC header for", path)
                filter_name = "Skip(512)"
            raw_sha1_obj.update(data)
        elif ext in [".v64", ".n64"]:
            filter_name = "ByteSwapWords"

        def is_sha1(name):
            if not len(name) == 40:
                return False
            name = name.lower()
            for c in name:
                if c not in "0123456789abcdef":
                    return False
            return True

        if filter_name:
            # We have a filter, so we must calculate checksum of filtered contents
            pass
        else:
            # Try to see if we can deduce the checksum of the contained file.
            # Supports symlinks to compressed files.
            real_path = os.path.realpath(archive.path)
            real_name = os.path.basename(real_path)
            real_name = real_name.lower()
            real_name, real_ext = os.path.splitext(real_name)
            if real_ext in [".xz", ".gz"]:
                if is_sha1(real_name):
                    if parent is not None:
                        # We assume this is the correct SHA-1, avoids having
                        # to decompress and calculate the SHA-1
                        sha1 = real_name
                    else:
                        # Assume we are not interested in the parent's SHA-1
                        sha1 = "ffffffffffffffffffffffffffffffffffffffff"

        if sha1 is None:
            if f is None:
                f = archive.open(path)
            while True:
                if self.stop_check():
                    return
                data = f.read(65536)
                if not data:
                    break
                raw_sha1_obj.update(data)
                if filter_name.startswith("Skip("):
                    filter_sha1_obj.update(data)
                    filter_size += len(data)
                elif filter_name == "ByteSwapWords":
                    # We don't really expect odd number of bytes when
                    # byteswapping words, but this handles the cases where we
                    # have "false positives" that aren't supposed to be
                    # byteswapped, and this prevents errors.
                    data_size = len(data)
                    for i in range(0, len(data), 2):
                        if data_size - i >= 2:
                            filter_sha1_obj.update(data[i + 1 : i + 2])
                            filter_sha1_obj.update(data[i : i + 1])
                            filter_size += 2
                        else:
                            filter_sha1_obj.update(data[i : i + 1])
                            filter_size += 1
            sha1 = raw_sha1_obj.hexdigest()
            filter_sha1 = filter_sha1_obj.hexdigest()

        if ext == ".rom":
            try:
                filter_data = ROMManager.decrypt_archive_rom(archive, path)
                filter_sha1 = filter_data["sha1"]
                filter_size = len(filter_data["data"])
            except Exception:
                import traceback

                traceback.print_exc()
                filter_sha1 = None
            if filter_sha1:
                if filter_sha1 != sha1:
                    print(
                        "[Files] Found encrypted rom {0} => {1}".format(
                            sha1, filter_sha1
                        )
                    )
                    # sha1 is now the decrypted sha1, not the actual sha1 of the
                    # file itself, a bit ugly, since md5 and crc32 are still
                    # encrypted hashes, but it works well with the kickstart
                    # lookup mechanism
                    # FIXME: Enable use of filter mechanism for Cloanto ROMs
                    sha1 = filter_sha1
                    # filter_name = "Cloanto"
            else:
                # If the ROM was encrypted and could not be decrypted, we
                # don't add it to the database. This way, the file will be
                # correctly added on later scans if rom.key is added to the
                # directory.
                return None

        if parent:
            path = "#/" + path.rsplit("#/", 1)[1]
        if parent is not None:
            # FIXME: size is incorrect here -- it's the size of the parent
            # file currently (not a big problem), setting it to -1 instead
            # for now.
            size = -1
        file_id = database.add_file(
            path=path, sha1=sha1, mtime=mtime, size=size, parent=parent
        )
        self.files_added += 1
        if parent is None:
            self.bytes_added += size

        if filter_name:
            if parent:
                # We want to add to the previous archive path
                pass
            else:
                # Reset path
                path = ""
            path += "#?Filter=" + filter_name
            # If not already in an archive (has a real file parent), set
            # parent to the real file
            database.add_file(
                path=path,
                sha1=filter_sha1,
                mtime=mtime,
                size=filter_size,
                parent=(parent or file_id),
            )

        if ext == ".rom":
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
