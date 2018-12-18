import hashlib
import json
import os
import shutil
import tempfile
import traceback
import unittest
import urllib.parse
import zlib
from typing import List, Dict

from fsbc.paths import Paths
from fsbc.resources import Resources
from fsbc.task import current_task, TaskFailure
from fsgs.archive import Archive
from fsgs.FSGSDirectories import FSGSDirectories
from fsgs.GameChangeHandler import GameChangeHandler
from fsgs.GameNameUtil import GameNameUtil
from fsgs.amiga import whdload
from fsgs.amiga.adffileextractor import ADFFileExtractor
from fsgs.amiga.amiga import Amiga
from fsgs.amiga.configwriter import ConfigWriter
from fsgs.amiga.fsuae import FSUAE
from fsgs.amiga.rommanager import ROMManager
from fsgs.amiga.roms import PICASSO_IV_74_ROM, CD32_FMV_ROM
from fsgs.amiga.workbench import WorkbenchExtractor
from fsgs.download import Downloader
from fsgs.drivers.gamedriver import GameDriver
from fsgs.knownfiles import ACTION_REPLAY_MK_III_3_17_ROM, \
    ACTION_REPLAY_MK_III_3_17_MOD_ROM, ACTION_REPLAY_MK_II_2_14_ROM, \
    ACTION_REPLAY_MK_II_2_14_MOD_ROM
from fsgs.network import is_http_url
from fsgs.option import Option
from fsgs.res import gettext


class LaunchHandler(object):

    def __init__(self, fsgs, config_name, config, game_paths, temp_dir=""):
        self.fsgs = fsgs
        self.fsgc = fsgs
        self.config_name = config_name
        self.config = config.copy()

        for remove_key in ["database_username", "database_password",
                           "database_username", "database_email",
                           "database_auth", "device_id"]:
            if remove_key in self.config:
                del self.config[remove_key]

        # make sure FS-UAE does not load other config files (Host.fs-uae)
        self.config["end_config"] = "1"

        self.game_paths = game_paths
        self.hd_requirements = set()
        for req in self.config.get(
                "hd_requirements", "").replace(",", ";").split(";"):
            req = req.strip()
            if req:
                self.hd_requirements.add(req)
        self.setpatch_installed = False
        # self.stop_flag = False

        self.temp_dir = temp_dir
        self.change_handler = None

        self.use_relative_paths = self.config.get(
            Option.RELATIVE_TEMP_FEATURE, "") == "1"

    @property
    def stop_flag(self):
        return current_task.stop_flag

    def on_progress(self, progress):
        # method can be overridden / replaced in instances
        pass

    def on_complete(self):
        # method can be overridden / replaced in instances
        pass

    def prepare(self):
        print("LaunchHandler.prepare")
        if not self.temp_dir:
            self.temp_dir = tempfile.mkdtemp(prefix="fs-uae-")
        print("temp dir", self.temp_dir)
        self.config["floppies_dir"] = self.temp_dir
        print("state dir", self.get_state_dir())
        self.config["state_dir"] = self.get_state_dir()
        self.config["save_states_dir"] = ""
        self.config["floppy_overlays_dir"] = ""
        self.config["flash_memory_dir"] = ""
        self.change_handler = GameChangeHandler(self.temp_dir)

        self.config["cdroms_dir"] = FSGSDirectories.get_cdroms_dir()
        self.config[
            "configurations_dir"] = FSGSDirectories.get_configurations_dir()
        self.config["controllers_dir"] = FSGSDirectories.get_controllers_dir()
        self.config["hard_drives_dir"] = FSGSDirectories.get_hard_drives_dir()
        self.config["kickstarts_dir"] = FSGSDirectories.get_kickstarts_dir()
        self.config["save_states_dir"] = FSGSDirectories.get_save_states_dir()
        self.config["themes_dir"] = FSGSDirectories.get_themes_dir()

        self.prepare_roms()
        if self.stop_flag:
            return
        self.prepare_floppies()
        if self.stop_flag:
            return
        self.prepare_cdroms()
        if self.stop_flag:
            return
        self.prepare_hard_drives()
        if self.stop_flag:
            return
        self.copy_hd_files()
        if self.stop_flag:
            return
        self.init_changes()
        if self.stop_flag:
            return
        self.prepare_theme()
        if self.stop_flag:
            return
        self.prepare_extra_settings()

    def run_sequence(self, start=True, cleanup=True):
        print("LaunchHandler.run_sequence")
        self.prepare()

        if not self.stop_flag:
            # too late to stop now...
            if start:
                self.run()
            self.update_changes()

        if cleanup:
            self.cleanup()

        print("calling LaunchHandler.on_complete")
        self.on_complete()

    def prepare_roms(self):
        print("LaunchHandler.prepare_roms")
        current_task.set_progress(gettext("Preparing kickstart ROMs..."))
        amiga_model = self.config.get("amiga_model", "A500")
        model_config = Amiga.get_model_config(amiga_model)

        roms = [("kickstart_file", model_config["kickstarts"])]
        if self.config["kickstart_ext_file"] or model_config["ext_roms"]:
            # not all Amigas have extended ROMs
            roms.append(("kickstart_ext_file", model_config["ext_roms"]))
        if amiga_model.lower() == "cd32/fmv":
            roms.append(("fvm_rom", [CD32_FMV_ROM]))

        if self.config["graphics_card"].lower().startswith("picasso-iv"):
            roms.append(("graphics_card_rom", [PICASSO_IV_74_ROM]))

        if self.config["accelerator"].lower() == "cyberstorm-ppc":
            roms.append(("accelerator_rom", ["cyberstormppc.rom"]))

        if self.config["freezer_cartridge"] == "action-replay-2":
            # Ideally, we would want to recognize ROMs based on zeroing the
            # first four bytes, but right now we simply recognize a common
            # additional version. freezer_cartridge_rom isn't a real option,
            # we just want to copy the rom file and let FS-UAE find it
            roms.append(("[freezer_cartridge]",
                         [ACTION_REPLAY_MK_II_2_14_ROM.sha1,
                          ACTION_REPLAY_MK_II_2_14_MOD_ROM.sha1]))
        elif self.config["freezer_cartridge"] == "action-replay-3":
            roms.append(("[freezer_cartridge]",
                         [ACTION_REPLAY_MK_III_3_17_ROM.sha1,
                          ACTION_REPLAY_MK_III_3_17_MOD_ROM.sha1]))

        for config_key, default_roms in roms:
            print("[ROM]", config_key, default_roms)
            src = self.config[config_key]
            if not src:
                for sha1 in default_roms:
                    print("[ROM] Trying", sha1)
                    if is_sha1(sha1):
                        rom_src = self.fsgs.file.find_by_sha1(sha1)
                        if rom_src:
                            src = rom_src
                            print("[ROM] Found", rom_src)
                            break
                    else:
                        # roms_dir = FSGSDirectories.get_kickstarts_dir()
                        # src = os.path.join(roms_dir, sha1)
                        # if os.path.exists(src):
                        #     break
                        # loop up file in roms dir instead
                        src = sha1
            elif src == "internal":
                continue
            elif src:
                src = Paths.expand_path(src)
            if not src:
                raise TaskFailure(
                    gettext("Did not find required Kickstart or "
                            "ROM for {}. Wanted one of these files: {}".format(
                                config_key, repr(default_roms))))

            use_temp_kickstarts_dir = False

            dest = os.path.join(self.temp_dir, os.path.basename(src))

            def lookup_rom_from_src(src):
                parts = src.split(":", 1)
                if len(parts) == 2 and len(parts[0]) > 1:
                    # src has a scheme (not a Windows drive letter). Assume
                    # we can find this file.
                    return src
                archive = Archive(src)
                if archive.exists(src):
                    return src
                dirs = [self.fsgs.amiga.get_kickstarts_dir()]
                for dir_ in dirs:
                    path = os.path.join(dir_, src)
                    print("[ROM] Checking", repr(path))
                    archive = Archive(path)
                    if archive.exists(path):
                        return path
                return None

            org_src = src
            src = lookup_rom_from_src(src)
            if not src and org_src == "cyberstormppc.rom":
                src = lookup_rom_from_src(
                    "ralphschmidt-cyberstorm-ppc-4471.rom")
                if not src:
                    for dir_ in FSGSDirectories.get_amiga_forever_directories():
                        path = os.path.join(
                            dir_, "Shared", "rom",
                            "ralphschmidt-cyberstorm-ppc-4471.rom")
                        if os.path.exists(path):
                            src = path
                            print("[ROM] Found", path)
                            break
                        else:
                            print("[ROM] Trying", path)
            stream = None
            try:
                stream = self.fsgs.file.open(src)
                if stream is None:
                    raise FileNotFoundError(src)
            except FileNotFoundError:
                raise TaskFailure(gettext(
                    "Cannot find required ROM "
                    "file: {name}".format(name=repr(org_src))))
            with open(dest, "wb") as f:
                if stream:
                    f.write(stream.read())
                else:
                    archive = Archive(src)
                    ROMManager.decrypt_archive_rom(archive, src, file=f)
                if use_temp_kickstarts_dir:
                    self.config[config_key] = os.path.basename(src)
                else:
                    self.config[config_key] = dest
            if use_temp_kickstarts_dir:
                self.config["kickstarts_dir"] = self.temp_dir

    @staticmethod
    def expand_default_path(src, default_dir):
        if "://" in src:
            return src, None
        src = Paths.expand_path(src, default_dir)
        archive = Archive(src)
        # if not archive.exists(src):
        #     dirs = [default_dir]
        #     for dir in dirs:
        #         path = os.path.join(dir, src)
        #         print("checking", repr(path))
        #         archive = Archive(path)
        #         if archive.exists(path):
        #         #if os.path.exists(path):
        #             src = path
        #             break
        #     else:
        #         raise Exception("Cannot find path for " + repr(src))
        return src, archive

    def prepare_floppy(self, key):
        src = self.config.get(key, "").strip()
        if not src:
            return

        src, archive = self.expand_default_path(
            src, self.fsgs.amiga.get_floppies_dir())
        dst_name = os.path.basename(src)
        current_task.set_progress(dst_name)

        if self.config["writable_floppy_images"] == "1" and \
                os.path.isfile(src):
            # the config value directly refers to a local file, and the config
            # value already refers to the file, but since we may have
            # changed floppy_dir and the path may be relative, we set the
            # resolved path directly
            self.config[key] = src
        else:
            dst = os.path.join(self.temp_dir, dst_name)
            self.fsgs.file.copy_game_file(src, dst)
            self.config[key] = os.path.basename(dst)

    def prepare_floppies(self):
        print("LaunchHandler.copy_floppies")
        current_task.set_progress(gettext("Preparing floppy images..."))
        # self.on_progress(gettext("Preparing floppy images..."))

        floppies = []
        for i in range(Amiga.MAX_FLOPPY_DRIVES):
            key = "floppy_drive_{0}".format(i)
            if self.config.get(key, ""):
                floppies.append(self.config[key])
            self.prepare_floppy(key)

        for i in range(Amiga.MAX_FLOPPY_IMAGES):
            key = "floppy_image_{0}".format(i)
            if self.config.get(key, ""):
                break
        else:
            print("floppy image list is empty")
            for j, floppy in enumerate(floppies):
                self.config["floppy_image_{0}".format(j)] = floppy

        max_image = -1
        for i in range(Amiga.MAX_FLOPPY_IMAGES):
            key = "floppy_image_{0}".format(i)
            self.prepare_floppy(key)
            if self.config.get(key, ""):
                max_image = i

        save_image = max_image + 1

        if self.config.get("save_disk", "") != "0":
            s = Resources("fsgs", "res").stream("amiga/adf_save_disk.dat")
            data = s.read()
            data = zlib.decompress(data)
            save_disk = os.path.join(self.temp_dir, "Save Disk.adf")
            with open(save_disk, "wb") as f:
                f.write(data)
            key = "floppy_image_{0}".format(save_image)
            self.config[key] = "Save Disk.adf"

    def prepare_cdroms(self):
        print("LaunchHandler.prepare_cdroms")
        if not self.config.get("cdrom_drive_count", ""):
            if self.config.get("cdrom_drive_0", "") or \
                    self.config.get("cdrom_image_0", ""):
                self.config["cdrom_drive_count"] = "1"

        cdrom_drive_0 = self.config.get("cdrom_drive_0", "")
        if cdrom_drive_0.startswith("game:"):
            scheme, dummy, game_uuid, name = cdrom_drive_0.split("/")
            file_list = self.get_file_list_for_game_uuid(game_uuid)
            for file_item in file_list:
                src = self.fsgs.file.find_by_sha1(file_item["sha1"])

                src, archive = self.expand_default_path(
                    src, self.fsgs.amiga.get_cdroms_dir())
                dst_name = file_item["name"]
                current_task.set_progress(dst_name)

                dst = os.path.join(self.temp_dir, dst_name)
                self.fsgs.file.copy_game_file(src, dst)

            cue_sheets = self.get_cue_sheets_for_game_uuid(game_uuid)
            for cue_sheet in cue_sheets:
                # FIXME: Try to get this to work with the PyCharm type checker
                # noinspection PyTypeChecker
                with open(os.path.join(self.temp_dir,
                                       cue_sheet["name"]), "wb") as f:
                    # noinspection PyTypeChecker
                    f.write(cue_sheet["data"].encode("UTF-8"))

            for i in range(Amiga.MAX_CDROM_DRIVES):
                key = "cdrom_drive_{0}".format(i)
                value = self.config.get(key, "")
                if value:
                    self.config[key] = os.path.join(
                        self.temp_dir, os.path.basename(value))

            for i in range(Amiga.MAX_CDROM_IMAGES):
                key = "cdrom_image_{0}".format(i)
                value = self.config.get(key, "")
                if value:
                    self.config[key] = os.path.join(
                        self.temp_dir, os.path.basename(value))

        cdroms = []
        for i in range(Amiga.MAX_CDROM_DRIVES):
            key = "cdrom_drive_{0}".format(i)
            if self.config.get(key, ""):
                cdroms.append(self.config[key])

        for i in range(Amiga.MAX_CDROM_IMAGES):
            key = "cdrom_image_{0}".format(i)
            if self.config.get(key, ""):
                break
        else:
            print("CD-ROM image list is empty")
            for j, cdrom in enumerate(cdroms):
                self.config["cdrom_image_{0}".format(j)] = cdrom

    def prepare_hard_drives(self):
        print("LaunchHandler.prepare_hard_drives")
        current_task.set_progress(gettext("Preparing hard drives..."))
        # self.on_progress(gettext("Preparing hard drives..."))
        for i in range(0, 10):
            self.prepare_hard_drive(i)

    def prepare_hard_drive(self, index):
        key = "hard_drive_{}".format(index)
        src = self.config.get(key, "")
        dummy, ext = os.path.splitext(src)
        ext = ext.lower()

        if is_http_url(src):
            name = src.rsplit("/", 1)[-1]
            name = urllib.parse.unquote(name)
            self.on_progress(gettext("Downloading {0}...".format(name)))
            dest = os.path.join(self.temp_dir, name)
            Downloader.install_file_from_url(src, dest)
            src = dest
        elif src.startswith("hd://game/"):
            self.unpack_game_hard_drive(index, src)
            self.disable_save_states()
            return
        elif src.startswith("hd://template/workbench/"):
            self.prepare_workbench_hard_drive(index, src)
            self.disable_save_states()
            return
        elif src.startswith("hd://template/empty/"):
            self.prepare_empty_hard_drive(index, src)
            self.disable_save_states()
            return

        if ext in Archive.extensions:
            print("zipped hard drive", src)
            self.unpack_hard_drive(index, src)
            self.disable_save_states()

        elif src.endswith("HardDrive"):
            print("XML-described hard drive", src)
            self.unpack_hard_drive(index, src)
            self.disable_save_states()
        else:
            src = Paths.expand_path(src)
            self.config[key] = src

    def disable_save_states(self):
        # Save states cannot currently be used with temporarily created
        # hard drives, as HD paths are embedded into the save states, and
        # restoring the save state causes problems.
        
        if self.config.get("unsafe_save_states") == "1":
            return
        self.config["save_states"] = "0"

    def prepare_workbench_hard_drive(self, i, src):
        # dir_name = "DH{0}".format(i)
        dir_name = src.rsplit("/", 1)[-1]
        dir_path = os.path.join(self.temp_dir, dir_name)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

        amiga_model = self.config.get("amiga_model", "A500")
        if amiga_model.startswith("A1200") or \
                amiga_model.startswith("A4000") or \
                amiga_model.startswith("A3000"):
            workbench = "Minimal Workbench v3.1"
        elif amiga_model == "A600":
            workbench = "Minimal Workbench v2.05"
        elif amiga_model == "A500+":
            workbench = "Minimal Workbench v2.04"
        else:
            workbench = "Minimal Workbench v1.3"
        
        print("Try to find pre-configured hard drive", workbench)
        src_dir = os.path.join(self.fsgs.amiga.get_hard_drives_dir(), workbench)
        if src_dir and os.path.exists(src_dir):
            print("found", src_dir)
            self.copy_folder_tree(src_dir, dir_path)
        else:
            print(" - not found -")
            raise Exception("Did not found pre-configured hard drive " +
                            repr(workbench))
            
        self.config["hard_drive_{0}".format(i)] = dir_path

    def prepare_empty_hard_drive(self, i, src):
        dir_name = src.rsplit("/", 1)[-1]
        # dir_name = "DH{0}".format(i)
        dir_path = os.path.join(self.temp_dir, dir_name)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        self.config["hard_drive_{0}".format(i)] = dir_path

    def get_file_list_for_game_uuid(self, game_uuid):
        # FIXME: This is an ugly hack, we should already be told what
        # database to use.
        try:
            game_database = self.fsgs.get_game_database()
            values = game_database.get_game_values_for_uuid(game_uuid)
        except LookupError:
            try:
                game_database = self.fsgs.game_database("CD32")
                values = game_database.get_game_values_for_uuid(game_uuid)
            except LookupError:
                game_database = self.fsgs.game_database("CDTV")
                values = game_database.get_game_values_for_uuid(game_uuid)
        file_list = json.loads(values["file_list"])
        return file_list

    def get_cue_sheets_for_game_uuid(self, game_uuid) -> List[Dict]:
        # FIXME: This is an ugly hack, we should already be told what
        # database to use.
        try:
            game_database = self.fsgs.get_game_database()
            values = game_database.get_game_values_for_uuid(game_uuid)
        except LookupError:
            try:
                game_database = self.fsgs.game_database("CD32")
                values = game_database.get_game_values_for_uuid(game_uuid)
            except LookupError:
                game_database = self.fsgs.game_database("CDTV")
                values = game_database.get_game_values_for_uuid(game_uuid)
        if not values.get("cue_sheets", ""):
            return []
        return json.loads(values["cue_sheets"])

    def unpack_game_hard_drive(self, drive_index, src):
        print("unpack_game_hard_drive", drive_index, src)
        scheme, dummy, dummy, game_uuid, drive = src.split("/")
        drive_prefix = drive + "/"
        dir_name = "DH{0}".format(drive_index)
        dir_path = os.path.join(self.temp_dir, dir_name)
        file_list = self.get_file_list_for_game_uuid(game_uuid)
        for file_entry in file_list:
            if self.stop_flag:
                return

            name = file_entry["name"]
            if not name.startswith(drive_prefix):
                continue

            # extract Amiga relative path and convert each path component
            # to host file name (where needed).

            amiga_rel_path = name[len(drive_prefix):]
            print("amiga_rel_path", amiga_rel_path)
            amiga_rel_parts = amiga_rel_path.split("/")
            for i, part in enumerate(amiga_rel_parts):
                # part can be blank if amiga_rel_parts is a directory
                # (ending with /)
                if part:
                    amiga_rel_parts[i] = amiga_filename_to_host_filename(part)
            amiga_rel_path = "/".join(amiga_rel_parts)

            dst_file = os.path.join(dir_path, amiga_rel_path)
            print(repr(dst_file))
            if name.endswith("/"):
                os.makedirs(Paths.str(dst_file))
                continue
            if not os.path.exists(os.path.dirname(dst_file)):
                os.makedirs(os.path.dirname(dst_file))
            sha1 = file_entry["sha1"]

            # current_task.set_progress(os.path.basename(dst_file))
            current_task.set_progress(amiga_rel_path)
            self.fsgs.file.copy_game_file("sha1://{0}".format(sha1), dst_file)

            # src_file = self.fsgs.file.find_by_sha1(sha1)
            # if not os.path.exists(os.path.dirname(dst_file)):
            #     os.makedirs(os.path.dirname(dst_file))
            # stream = self.fsgs.file.open(src_file)
            # # archive = Archive(src_file)
            # # f = archive.open(src_file)
            # data = stream.read()
            # assert hashlib.sha1(data).hexdigest() == sha1
            # with open(dst_file, "wb") as out_file:
            #     out_file.write(data)

            # noinspection SpellCheckingInspection
            metadata = [
                "----rwed", " ", "2000-01-01 00:00:00.00", " ", "", "\n"]
            if "comment" in file_entry:
                metadata[4] = self.encode_file_comment(file_entry["comment"])
            with open(dst_file + ".uaem", "wb") as out_file:
                out_file.write("".join(metadata).encode("UTF-8"))

        if self.use_relative_paths:
            self.config["hard_drive_{0}".format(drive_index)] = dir_name
        else:
            self.config["hard_drive_{0}".format(drive_index)] = dir_path

    @staticmethod
    def encode_file_comment(comment):
        result = []
        # raw = 0
        for c in comment:
            # if c == '%':
            #     result.append("%")
            #     raw = 2
            # elif raw:
            #     result.append(c)
            #     raw = raw - 1
            # else:
            #     result.append("%{0:x}".format(ord(c)))
            result.append("%{0:x}".format(ord(c)))
        return "".join(result)

    def unpack_hard_drive(self, i, src):
        src, archive = self.expand_default_path(
            src, self.fsgs.amiga.get_hard_drives_dir())

        dir_name = "DH{0}".format(i)
        dir_path = os.path.join(self.temp_dir, dir_name)

        self.unpack_archive(src, dir_path)
        self.config["hard_drive_{0}".format(i)] = dir_path

    # def create_devs_dir(self):
    #     devs_dir = os.path.join(dest_dir, "Devs")
    #     if not os.path.exists(devs_dir):
    #         os.makedirs(devs_dir)
    #
    # def create_fonts_dir(self):
    #     fonts_dir = os.path.join(dest_dir, "Fonts")
    #     if not os.path.exists(fonts_dir):
    #         os.makedirs(fonts_dir)

    def copy_hd_files(self):
        whdload_args = self.config.get("x_whdload_args", "").strip()
        hdinst_args = self.config.get("x_hdinst_args", "").strip()
        hd_startup = self.config.get("hd_startup", "").strip()

        if not whdload_args and not hdinst_args and not hd_startup:
            return

        dest_dir = os.path.join(self.temp_dir, "DH0")
        if not self.config.get("hard_drive_0", ""):
            self.config["hard_drive_0"] = dest_dir
            self.config["hard_drive_0_label"] = "Workbench"

        print("copy_hd_files, dest_dir = ", dest_dir)

        s_dir = os.path.join(dest_dir, "S")
        if not os.path.exists(s_dir):
            os.makedirs(s_dir)
        libs_dir = os.path.join(dest_dir, "Libs")
        if not os.path.exists(libs_dir):
            os.makedirs(libs_dir)

        devs_dir = os.path.join(dest_dir, "Devs")
        if not os.path.exists(devs_dir):
            os.makedirs(devs_dir)
        fonts_dir = os.path.join(dest_dir, "Fonts")
        if not os.path.exists(fonts_dir):
            os.makedirs(fonts_dir)

        if hd_startup:
            self.config["hard_drive_0_priority"] = "6"
            # don't copy setpatch by default, at least not yet
            pass
        else:
            self.hd_requirements.add("setpatch")
            self.copy_setpatch(dest_dir)

        amiga_model = self.config.get("amiga_model", "A500").upper()
        if amiga_model in ["A500+", "A600"]:
            workbench_version = "2.04"
        elif amiga_model.startswith("A1200"):
            workbench_version = "3.0"
        elif amiga_model.startswith("A4000"):
            workbench_version = "3.0"
        else:
            workbench_version = None

        if "workbench" in self.hd_requirements:
            if not workbench_version:
                raise Exception(
                    "Unsupported workbench version for hd_requirements")
            extractor = WorkbenchExtractor(self.fsgs)
            extractor.install_version(workbench_version, dest_dir)
            # install_workbench_files(self.fsgs, dest_dir, workbench_version)

        for req in self.hd_requirements:
            if "/" in req:
                # assume a specific workbench file
                extractor = WorkbenchExtractor(self.fsgs)
                extractor.install_version(
                    workbench_version, dest_dir, [req],
                    install_startup_sequence=False)

        if whdload_args:
            self.copy_whdload_files(dest_dir, s_dir)
        elif hdinst_args:
            self.write_startup_sequence(s_dir, hdinst_args)
        elif hd_startup:
            self.write_startup_sequence(s_dir, hd_startup)

        system_configuration_file = os.path.join(
            devs_dir, "system-configuration")
        if not os.path.exists(system_configuration_file):
            with open(system_configuration_file, "wb") as f:
                f.write(system_configuration)

    def copy_whdload_files(self, dest_dir, s_dir):
        whdload_args = self.config.get("x_whdload_args", "").strip()
        if not whdload_args:
            return
        print("[WHDLOAD] LaunchHandler.copy_whdload_files")
        if self.config.get(Option.WHDLOAD_PRELOAD, "") != "0":
            if " PRELOAD" not in whdload_args.upper():
                print("[WHDLOAD] Adding PRELOAD argument")
                whdload_args += " PRELOAD"

        current_task.set_progress(gettext("Preparing WHDLoad..."))
        # self.on_progress(gettext("Preparing WHDLoad..."))
        print("[WHDLOAD] copy_whdload_files, dest_dir = ", dest_dir)

        whdload_dir = ""
        slave_original_name = whdload_args.split(" ", 1)[0]
        slave = slave_original_name.lower()
        found_slave = False
        for dir_path, dir_names, file_names in os.walk(dest_dir):
            for name in file_names:
                if name.lower() == slave:
                    print("[WHDLOAD] Found", name)
                    found_slave = True
                    whdload_dir = dir_path[len(dest_dir):]
                    whdload_dir = whdload_dir.replace("\\", "/")
                    if not whdload_dir:
                        # slave was found in root directory
                        pass
                    elif whdload_dir[0] == "/":
                        whdload_dir = whdload_dir[1:]
                    break
            if found_slave:
                break
        if not found_slave:
            raise Exception(
                "Did not find the specified WHDLoad slave {}. "
                "Check the WHDLoad arguments".format(repr(slave_original_name)))
        print("[WHDLOAD] Slave directory:", repr(whdload_dir))
        print("[WHDLOAD] Slave arguments:", whdload_args)

        self.copy_whdload_kickstart(
            dest_dir, "kick33180.A500",
            ["11f9e62cf299f72184835b7b2a70a16333fc0d88"])
        self.copy_whdload_kickstart(
            dest_dir, "kick34005.A500",
            ["891e9a547772fe0c6c19b610baf8bc4ea7fcb785"])
        self.copy_whdload_kickstart(
            dest_dir, "kick40068.A1200",
            ["e21545723fe8374e91342617604f1b3d703094f1"])
        self.copy_whdload_kickstart(
            dest_dir, "kick40068.A4000",
            ["5fe04842d04a489720f0f4bb0e46948199406f49"])
        whdload.create_prefs_file(
            self.config, os.path.join(s_dir, "WHDLoad.prefs"))

        whdload_version = self.config["x_whdload_version"]
        if not whdload_version:
            whdload_version = whdload.default_whdload_version

        for key, value in whdload.binaries[whdload_version].items():
            self.install_whdload_file(key, dest_dir, value)
        for key, value in whdload.support_files.items():
            self.install_whdload_file(key, dest_dir, value)

        if self.config.get("__netplay_game", ""):
            print("[WHDLOAD] Key file is not copied in net play mode")
        else:
            key_file = os.path.join(
                self.fsgs.amiga.get_base_dir(), "WHDLoad.key")
            if os.path.exists(key_file):
                print("found WHDLoad.key at ", key_file)
                shutil.copy(key_file, os.path.join(s_dir, "WHDLoad.key"))
            else:
                print("[WHDLOAD] Key file not found in base dir (FS-UAE dir)")

            # temporary feature, at least until it's possible to set more
            # WHDLoad settings directly in the Launcher
            prefs_file = os.path.join(
                self.fsgs.amiga.get_base_dir(), "WHDLoad.prefs")
            if os.path.exists(prefs_file):
                print("found WHDLoad.prefs at ", prefs_file)
                shutil.copy(prefs_file, os.path.join(s_dir, "WHDLoad.prefs"))
            else:
                print("[WHDLOAD] Key file not found in base dir (FS-UAE dir)")

        if self.config.get("__netplay_game", ""):
            print("[WHDLOAD] WHDLoad base dir is not copied in net play mode")
        else:
            src_dir = self.get_whdload_dir()
            if src_dir and os.path.exists(src_dir):
                print("[WHDLOAD] WHDLoad base dir exists, copying resources...")
                self.copy_folder_tree(src_dir, dest_dir)

        # icon = self.config.get("__whdload_icon", "")
        icon = ""
        if icon:
            shutil.copy(os.path.expanduser("~/kgiconload"), 
                        os.path.join(dest_dir, "C", "kgiconload"))
            icon_path = os.path.join(dest_dir, icon)
            print("[WHDLOAD] Create icon at ", icon_path)
            create_slave_icon(icon_path, whdload_args)
            self.write_startup_sequence(
                s_dir,
                "cd \"{0}\"\n"
                "kgiconload {1}\n"
                "uae-configuration SPC_QUIT 1\n".format(
                    whdload_dir, os.path.basename(icon)))
        else:
            self.write_startup_sequence(
                s_dir, whdload_sequence.format(whdload_dir, whdload_args))

    def get_whdload_dir(self):
        path = self.config.get(Option.WHDLOAD_BOOT_DIR)
        return path

    def write_startup_sequence(self, s_dir, command):
        # FIXME: semi-colon is used in WHDLoad CONFIG options...
        command = "\n".join([x.strip() for x in command.split(";")])
        startup_sequence = os.path.join(s_dir, "Startup-Sequence")
        # if True:
        if not os.path.exists(startup_sequence):
            with open(startup_sequence, "wb") as f:
                if "setpatch" in self.hd_requirements:
                    if self.setpatch_installed:
                        f.write(setpatch_found_sequence.replace(
                                "\r\n", "\n").encode("ISO-8859-1"))
                    else:
                        f.write(setpatch_not_found_sequence.replace(
                                "\r\n", "\n").encode("ISO-8859-1"))
                f.write(command.replace(
                        "\r\n", "\n").encode("ISO-8859-1"))

        # The User-Startup file is useful if the user has provided a
        # base WHDLoad directory with an existing startup-sequence
        user_startup = os.path.join(s_dir, "User-Startup")
        with open(user_startup, "ab") as f:
            f.write(command.replace(
                    "\r\n", "\n").encode("ISO-8859-1"))

    def install_whdload_file(self, sha1, dest_dir, rel_path):
        abs_path = os.path.join(dest_dir, rel_path)
        name = os.path.basename(rel_path)
        self.on_progress(gettext("Downloading {0}...".format(name)))
        Downloader.install_file_by_sha1(sha1, name, abs_path)

    def copy_setpatch(self, base_dir):
        dest = os.path.join(base_dir, "C")
        if not os.path.exists(dest):
            os.makedirs(dest)
        dest = os.path.join(dest, "SetPatch")
        for checksum in workbench_disks_with_setpatch_39_6:
            path = self.fsgs.file.find_by_sha1(checksum)
            if path:
                print("found WB DISK with SetPatch 39.6 at", path)
                try:
                    input_stream = self.fsgs.file.open(path)
                except Exception:
                    traceback.print_exc()
                else:
                    wb_data = input_stream.read()
                # archive = Archive(path)
                # if archive.exists(path):
                #     f = archive.open(path)
                #     wb_data = f.read()
                #     f.close()
                    if self.extract_setpatch_39_6(wb_data, dest):
                        print("SetPatch installed")
                        self.setpatch_installed = True
                        break
                    else:
                        print("WARNING: extract_setpatch_39_6 returned False")
                # else:
                #     print("oops, path does not exist")
        else:
            print("WARNING: did not find SetPatch 39.6")

    @staticmethod
    def extract_setpatch_39_6(wb_data, dest):
        extractor = ADFFileExtractor(wb_data)
        try:
            setpatch_data = extractor.extract_file("C/SetPatch")
        except KeyError:
            return False
        s = hashlib.sha1()
        s.update(setpatch_data)
        print(s.hexdigest())
        # noinspection SpellCheckingInspection
        if s.hexdigest() != "4d4aae988310b07726329e436b2250c0f769ddff":
            return False
        with open(dest, "wb") as f:
            f.write(setpatch_data)
        return True

    def copy_whdload_kickstart(self, base_dir, name, checksums):
        dest = os.path.join(base_dir, "Devs", "Kickstarts")
        if not os.path.exists(dest):
            os.makedirs(dest)
        dest = os.path.join(dest, name)
        for checksum in checksums:
            # print("find kickstart with sha1", checksum)
            path = self.fsgs.file.find_by_sha1(checksum)
            if path:  # and os.path.exists(path):
                print("found kickstart for", name, "at", path)
                archive = Archive(path)
                if archive.exists(path):
                    with open(dest, "wb") as f:
                        ROMManager.decrypt_archive_rom(archive, path, file=f)
                    print(repr(dest))
                    break
                else:
                    stream = self.fsgs.file.open(path)
                    if stream is None:
                        raise Exception("Cannot find kickstart " + repr(path))
                    with open(dest, "wb") as f:
                        f.write(stream.read())

        else:
            print("did not find kickstart for", name)

    def get_state_dir(self):
        return self.game_paths.get_state_dir()

    def init_changes(self):
        print("LaunchHandler.init_changes")
        self.on_progress(gettext("Restoring changes..."))
        self.change_handler.init(
            self.get_state_dir(), ignore=["*.uss", "*.sdf"])

    def update_changes(self):
        print("LaunchHandler.update_changes")
        self.on_progress(gettext("Saving changes..."))
        self.change_handler.update(self.get_state_dir())

    def cleanup(self):
        print("LaunchHandler.cleanup")
        if os.environ.get("FSGS_CLEANUP", "") == "0":
            print("[DRIVER] NOTICE: keeping temp files around...")
            return

        self.on_progress(gettext("Cleaning up..."))
        # self.delete_tree(self.temp_dir)
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        state_dir = self.get_state_dir()
        try:
            # this will only succeed if the directory is empty -we don't
            # want to leave unnecessary empty state directories
            os.rmdir(state_dir)
            print("removed", repr(state_dir))
            # also try to remove the parent (letter dir)
            os.rmdir(os.path.dirname(state_dir))
            print("removed", repr(os.path.dirname(state_dir)))
        except OSError:
            # could not delete directories - ok - probably has content
            pass

    def prepare_theme(self):
        # path = self.game_paths.get_theme_path()
        # if path:
        #     self.config["theme"] = path
        pass

    def prepare_extra_settings(self):
        prefix = self.config.get("screenshots_output_prefix", "")
        if prefix:
            return
        # name = self.config.get("floppy_drive_0", "")
        # if not name:
        #     name = self.config.get("hard_drive_0", "")
        # if not name:
        #     name = self.config.get("cdrom_drive_0", "")
        # if not name:
        #     name = self.config.get("floppy_image_0", "")
        name = self.config_name
        if not name:
            name = "fs-uae"
        name, variant = GameNameUtil.extract_names(name)
        name = GameNameUtil.create_cmpname(name)
        self.config["screenshots_output_prefix"] = name

    def create_config(self):
        config = ConfigWriter(self.config).create_fsuae_config()
        return config

    def write_config(self, f):
        config_lines = self.create_config()
        for line in config_lines:
            f.write(line)
            f.write("\n")

    def write_config_to_file(self, path):
        with open(path, "wb") as f:
            self.write_config(f)

    def run(self):
        print("LaunchHandler.run")
        # self.on_progress(gettext("Starting FS-UAE..."))
        # current_task.set_progress(gettext("Starting FS-UAE..."))
        current_task.set_progress("__run__")
        config = self.create_config()
        if self.use_relative_paths:
            process, config_file = FSUAE.start_with_config(
                config, cwd=self.temp_dir)
        else:
            process, config_file = FSUAE.start_with_config(config)
        pid_file = self.fsgc.settings[Option.EMULATOR_PID_FILE]
        GameDriver.write_emulator_pid_file(pid_file, process)
        process.wait()
        GameDriver.remove_emulator_pid_file(pid_file)
        print("LaunchHandler.start is done")
        if os.environ.get("FSGS_CLEANUP", "") == "0":
            print("Not removing", config_file)
        else:
            print("removing", config_file)
            try:
                os.remove(config_file)
            except Exception:
                print("could not remove config file", config_file)

    def unpack_archive(self, path, destination):
        print("unpack", path, "to", destination)
        archive = Archive(path)
        print(archive)
        print(archive.get_handler())
        for name in archive.list_files():
            if self.stop_flag:
                return

            print(name)
            n = name[len(path) + 2:]
            out_path = os.path.join(destination, n)
            print("out path", out_path)

            if name.endswith("/"):
                os.makedirs(out_path)
            else:
                if not os.path.exists(os.path.dirname(out_path)):
                    os.makedirs(os.path.dirname(out_path))
                f = archive.open(name)
                with open(out_path, "wb") as out_f:
                    while True:
                        data = f.read(65536)
                        if not data:
                            break
                        out_f.write(data)

    def copy_folder_tree(self, source_path, dest_path, overwrite=False):
        for item in os.listdir(source_path):
            if self.stop_flag:
                return
            if item[0] == ".":
                continue
            item_path = os.path.join(source_path, item)
            dest_item_path = os.path.join(dest_path, item)
            if os.path.isdir(item_path):
                if not os.path.exists(dest_item_path):
                    os.makedirs(dest_item_path)
                self.copy_folder_tree(item_path, dest_item_path)
                if self.stop_flag:
                    return
            else:
                if overwrite or not os.path.exists(dest_item_path):
                    print("copy", repr(item_path), "to", repr(dest_item_path))
                    shutil.copy(item_path, dest_item_path)


def amiga_filename_to_host_filename(amiga_name, ascii_only=False):
    """
    Converted from FS-UAE C code (src/od-fs/fsdb-host.py)
    @author: TheCyberDruid
    """
    length = len(amiga_name)

    replace_1 = -1
    replace_2 = -1

    check = amiga_name[:3].upper()
    dot_pos = -1
    if check in ["AUX", "CON", "PRN", "NUL"]:
        dot_pos = 4
    elif check in ["LPT", "COM"] and length >= 4 and amiga_name[3].isdigit():
        dot_pos = 5
    if (dot_pos > -1 and (length == (dot_pos - 1) or (
            length > dot_pos and amiga_name[dot_pos] == "."))):
        replace_1 = 2

    if amiga_name[-1] == "." or amiga_name[-1] == " ":
        replace_2 = length - 1

    i = 0
    filename = ""
    for c in amiga_name:
        x = ord(c)
        replace = False
        if i == replace_1:
            replace = True
        elif i == replace_2:
            replace = True
        elif x < 32:
            replace = True
        elif ascii_only and x > 127:
            replace = True

        if not replace:
            for evil in EVIL_CHARS:
                if evil == c:
                    replace = True
                    break
        if (i == length - 1) and amiga_name[-5:] == ".uaem":
            replace = True

        if replace:
            filename += "%" + "%02x" % ord(c)
        else:
            filename += c

        i += 1

    return filename

EVIL_CHARS = '%\\*?\"/|<>'

system_configuration = (
    b"\x08\x00\x00\x05\x00\x00\x00\x00\x00\x00\xc3"
    b"P\x00\x00\x00\x00\x00\t'\xc0\x00\x00\x00\x01\x00\x00N \x00\x00\x00\x00"
    b"\xc0\x00@\x00p\x00\xb0\x00<\x00L\x00?\x00C\x00\x1f\xc0 \xc0\x1f\xc0 \x00"
    b"\x0f\x00\x11\x00\r\x80\x12\x80\x04\xc0\t@\x04`\x08\xa0\x00 \x00@\x00\x00"
    b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
    b"\x00\x00\x00\x00\xff\x00\x0eD\x00\x00\x0e\xec\x00\x01\n\xaa\x00\x00\x0f"
    b"\xff\x06\x8b\x00\x00\x00\x81\x00,\x00\x00\x00\x00generic\x00\x00\x00\x00"
    b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
    b"\x00\x00\x00\x00\x00\x00\x00\x00\x05\x00K\x00\x00\x00\x00\x00\x00\x00\x07"
    b"\x00 \x00B\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
    b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
    b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00"
    b"\x00")

# noinspection SpellCheckingInspection
workbench_disks_with_setpatch_39_6 = [
    # Workbench v3.0 rev 39.29 (1992)(Commodore)(A1200-A4000)(M10)
    # (Disk 1 of 6)(Install).adf
    "ba24b4172339b9198e4f724a6804d0c6eb5e394b",
    # Workbench v3.0 rev 39.29 (1992)(Commodore)(A1200-A4000)(M10)
    # (Disk 1 of 6)(Install)[a].adf
    "c0781dece2486b54e15ce54a9b24dec6d9429421",
    # Workbench v3.0 rev 39.29 (1992)(Commodore)(A1200-A4000)(M10)
    # (Disk 1 of 6)(Install)[m drive definitions].adf
    "7eeb2511ce34f8d3f09efe82b290bddeb899d237",
    # Workbench v3.0 rev 39.29 (1992)(Commodore)(A1200-A4000)(M10)
    # (Disk 1 of 6)(Install)[m2].adf
    "7271d7db4472e10fbe4b266278e16f03336c14e3",
    # Workbench v3.0 rev 39.29 (1992)(Commodore)(A1200-A4000)(M10)
    # (Disk 1 of 6)(Install)[m3].adf
    "92c2f33bb73e1bdee5d9a0dc0f5b09a15524f684",
    # Workbench v3.0 rev 39.29 (1992)(Commodore)(A1200-A4000)(M10)
    # (Disk 2 of 6)(Workbench)[!].adf
    "e663c92a9c88fa38d02bbb299bea8ce70c56b417",
    # Workbench v3.0 rev 39.29 (1992)(Commodore)(A1200-A4000)(M10)
    # (Disk 2 of 6)(Workbench)[a2].adf
    "65ab988e597b456ac40320f88a502fc016d590aa",
    # Workbench v3.0 rev 39.29 (1992)(Commodore)(A1200-A4000)(M10)
    # (Disk 2 of 6)(Workbench)[a].adf
    "9496daa66e6b2f4ddde4fa2580bb3983a25e3cd2",
    # Workbench v3.0 rev 39.29 (1992)(Commodore)(A1200-A4000)(M10)
    # (Disk 2 of 6)(Workbench)[m2].adf
    "cf2f24cf5f5065479476a38ec8f1016b1f746884",
    # Workbench v3.0 rev 39.29 (1992)(Commodore)(A1200-A4000)(M10)
    # (Disk 2 of 6)(Workbench)[m3].adf
    "0e7f30223af254df0e2b91ea409f35c56d6164a6",
    # Workbench v3.0 rev 39.29 (1992)(Commodore)(A1200-A4000)(M10)
    # (Disk 2 of 6)(Workbench)[m4].adf
    "08c4afde7a67e6aaee1f07af96e95e9bed897947",
    # amiga-os-300-workbench.adf
    # Workbench v3.0 rev 39.29 (1992)(Commodore)(A1200-A4000)(M10)
    # (Disk 2 of 6)(Workbench)[m5].adf
    "4f4770caae5950eca4a2720e0424df052ced6a32",
    # Workbench v3.0 rev 39.29 (1992)(Commodore)(A1200-A4000)(M10)
    # (Disk 2 of 6)(Workbench)[m].adf
    "53086c3e44ec2d34e60ab65af71fb11941f4e0af",
]

setpatch_found_sequence = """
C:SetPatch
"""

setpatch_not_found_sequence = """
echo "Warning: SetPatch (39.6) not found."
echo "Make sure a WB 3.0 disk is scanned in FS-UAE Launcher"
echo "and the file will automatically be copied from the disk."
EndIF
"""

whdload_sequence = """
cd "{0}"
WHDLoad {1}
uae-configuration SPC_QUIT 1
"""

# noinspection SpellCheckingInspection
base_icon = \
    b"\xe3\x10\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x006\x00" \
    b"\x17\x00\x04\x00\x01\x00\x01\x00\x02\x1a\x98\x00\x00\x00\x00\x00" \
    b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00" \
    b"\x00\x04\x00\x00\t\x01l\x00\x01\xa5\x9c\x80\x00\x00\x00\x80\x00" \
    b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x10\x00\x00\x00" \
    b"\x00\x00\x006\x00\x16\x00\x02\x00\x08\xce \x03\x00\x00\x00\x00\x00" \
    b"\x00\x00\x00\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00\x0c\x00" \
    b"\x00\x00\x00\x00\x00\x00\x0c\x00\x00\x00\x00\x00\x00\x00\x0c\x00" \
    b"\x00\x00\x00\x00\x00\x00\x0c\x00\x00\x00\x00\x00\x00\x00\x0c\x00" \
    b"\x03\xf0\x0f\xff\xe0\x00\x0c\x00\x02\x080\x00\x1c\x00\x0c\x00\x02" \
    b"\x07\xc0\x00\x03\x80\x0c\x00\x02\x00\x00\x00\x00`\x0c\x00\x02\x00" \
    b"\x00\x00\x00\x10\x0c\x00\x02\x00\x00\x00\x00\x08\x0c\x00\x02\x07" \
    b"\xc0\x00\x1f\xc4\x0c\x00\x02\x08 \x00 2\x0c\x00\x03\xf0\x18\x00" \
    b"\xc0\r\x0c\x00\x00\x00\x06\x03\x00\x03\x0c\x00\x00\x00\x02\x02" \
    b"\x00\x00\x0c\x00\x00\x00\x02\x02\x00\x00\x0c\x00\x00\x00\x02\x02" \
    b"\x00\x00\x0c\x00\x00\x00\x03\xfe\x00\x00\x0c\x00\x00\x00\x00\x00" \
    b"\x00\x00\x0c\x00\x7f\xff\xff\xff\xff\xff\xfc\x00\xff\xff\xff\xff" \
    b"\xff\xff\xf8\x00\xd5UUUUUP\x00\xd5UUUUUP\x00\xd5UUUUUP\x00\xd5UUU" \
    b"UUP\x00\xd5UUUUUP\x00\xd4\x05P\x00\x15UP\x00\xd4\x05@\x00\x01UP" \
    b"\x00\xd4\x00\x00\x00\x00UP\x00\xd4\x00\x00\x00\x00\x15P\x00\xd4" \
    b"\x00\x00\x00\x00\x05P\x00\xd4\x00\x00\x00\x00\x05P\x00\xd4\x00" \
    b"\x00\x00\x00\x01P\x00\xd4\x05@\x00\x15AP\x00\xd4\x05@\x00\x15PP" \
    b"\x00\xd5UP\x00UTP\x00\xd5UT\x01UUP\x00\xd5UT\x01UUP\x00\xd5UT" \
    b"\x01UUP\x00\xd5UT\x01UUP\x00\xd5UUUUUP\x00\x80\x00\x00\x00\x00" \
    b"\x00\x00\x00"


def char(v):
    return chr(v)


def write_number(f, n):
    f.write(char((n & 0xff000000) >> 3))
    f.write(char((n & 0x00ff0000) >> 2))
    f.write(char((n & 0x0000ff00) >> 1))
    f.write(char((n & 0x000000ff) >> 0))


def write_string(f, s):
    write_number(f, len(s) + 1)
    f.write(s)
    f.write("\0")


def create_slave_icon(path, whdload_args):
    default_tool = "DH0:/C/WHDLoad"
    # FIXME: handle "" around slave name?
    # args = whdload_args.split(" ")
    tool_types = whdload_args.split(" ")
    tool_types[0] = "SLAVE=" + tool_types[0]

    with open(path, "wb") as f:
        f.write(base_icon)
        write_string(f, default_tool)
        write_number(f, (len(tool_types) + 1) * 4)
        for tool_type in tool_types:
            write_string(f, tool_type)
        f.close()


def is_sha1(s):
    if len(s) != 40:
        return False
    for c in s:
        if c not in "0123456789abcdef":
            return False
    return True


class TestCase(unittest.TestCase):

    # noinspection SpellCheckingInspection
    def test_convert_amiga_file_name(self):
        result = amiga_filename_to_host_filename("pro.i*riska")
        self.assertEquals(result, "pro.i%2ariska")

    # noinspection SpellCheckingInspection
    def test_convert_amiga_file_name_2(self):
        result = amiga_filename_to_host_filename("mypony.uaem")
        self.assertEquals(result, "mypony.uae%6d")

    def test_convert_amiga_file_name_short(self):
        result = amiga_filename_to_host_filename("t")
        self.assertEquals(result, "t")

    def test_convert_amiga_file_name_short_2(self):
        result = amiga_filename_to_host_filename("t ")
        self.assertEquals(result, "t%20")

    def test_convert_amiga_file_name_lpt1(self):
        result = amiga_filename_to_host_filename("LPT1")
        self.assertEquals(result, "LP%541")

    def test_convert_amiga_file_name_aux(self):
        result = amiga_filename_to_host_filename("AUX")
        self.assertEquals(result, "AU%58")

if __name__ == '__main__':
    unittest.main()
