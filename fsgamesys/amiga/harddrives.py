from os import path
import hashlib
import os
from typing import Optional

from fsgamesys.amiga.amiga import Amiga
from fsgamesys.amiga.amigaconfig import AmigaConfig
from fsgamesys.amiga.amigaconstants import AmigaConstants
from fsgamesys.amiga.config import Config
from fsgamesys.amiga.launchhandler import (
    amiga_path_to_host_path,
    encode_file_comment,
    system_configuration,
)
from fsgamesys.amiga.types import ConfigType, FilesType
from fsgamesys.amiga.whdload import prepare_whdload_system_volume
from fsgamesys.amiga.xpkmaster import prepare_xpkmaster_files
from fsgamesys.network import is_http_url


def prepare_amiga_hard_drives(config: ConfigType, files):
    for i in range(Amiga.MAX_HARD_DRIVES):
        prepare_amiga_hard_drive(config, i, files)

    if not Config(config).whdload_args():
        # The WHDLoad override setting and config key does not quite
        # follow the usual semantics of configs/settings unfortunately, so
        # we really want whdload_quit_key to be cleared when not using
        # WHDLoad. Otherwise the emulator will try to quit everything with
        # the WHDLoad quit key (when overriden).
        Config(config).set_whdload_quit_key("")


def maybe_disable_save_states(config: ConfigType):
    # Save states cannot currently be used with temporarily created
    # hard drives, as HD paths are embedded into the save states, and
    # restoring the save state causes problems.

    if Config(config).unsafe_save_states():
        # User explicitly allows unsafe save states, not disabling
        return
    Config(config).set_save_states(False)


def prepare_amiga_hard_drive(config: ConfigType, drive_index: int, files):
    src = Config(config).hard_drive_n(drive_index)
    if not src:
        return

    if is_http_url(src):
        # name = src.rsplit("/", 1)[-1]
        # name = unquote(name)
        # self.on_progress(gettext("Downloading {0}...".format(name)))
        # dest = os.path.join(self.temp_dir, name)
        # Downloader.install_file_from_url(src, dest)
        # src = dest
        raise NotImplementedError()
    elif src.startswith("hd://game/"):
        prepare_game_hard_drive(config, drive_index, src, files)
        maybe_disable_save_states(config)
    elif src.startswith("file_list:"):
        prepare_game_hard_drive(config, drive_index, src, files)
        maybe_disable_save_states(config)
    elif src.startswith("hd://template/workbench/"):
        # self.prepare_workbench_hard_drive(drive_index, src)
        raise NotImplementedError()
        maybe_disable_save_states(config)
    elif src.startswith("hd://template/empty/"):
        # self.prepare_empty_hard_drive(drive_index, src)
        raise NotImplementedError()
        maybe_disable_save_states(config)
    else:
        # raise NotImplementedError()
        # dest_dir = "DH0"
        configKey = "hard_drive_{}".format(drive_index)
        # if not config.get(configKey, ""):
        config[configKey] = src

        # if ext in Archive.extensions:
        #     print("zipped hard drive", src)
        #     self.unpack_hard_drive(index, src)
        #     self.disable_save_states()

        # elif src.endswith("HardDrive"):
        #     print("XML-described hard drive", src)
        #     self.unpack_hard_drive(index, src)
        #     self.disable_save_states()
        # else:
        #     src = Paths.expand_path(src)
        #     self.config[key] = src

    if drive_index == 0:
        prepare_dh0_files(config, files)


# def get_file_list_for_game_uuid(game_uuid):
#     # FIXME: This is an ugly hack, we should already be told what
#     # database to use.
#     try:
#         game_database = self.fsgs.get_game_database()
#         values = game_database.get_game_values_for_uuid(game_uuid)
#     except LookupError:
#         try:
#             game_database = self.fsgs.game_database("CD32")
#             values = game_database.get_game_values_for_uuid(game_uuid)
#         except LookupError:
#             game_database = self.fsgs.game_database("CDTV")
#             values = game_database.get_game_values_for_uuid(game_uuid)
#     file_list = json.loads(values["file_list"])
#     return file_list


def prepare_dh0_files(config: ConfigType, files: FilesType):
    whdload_args = Config(config).whdload_args()
    hdinst_args = Config(config).hdinst_args()
    hd_startup = Config(config).hdinst_args()

    if not whdload_args and not hdinst_args and not hd_startup:
        return

    # dest_dir = os.path.join(self.temp_dir, "DH0")
    # dest_dir = "HardDrives/DH0"
    dest_dir = "DH0"
    if not config.get("hard_drive_0", ""):
        config["hard_drive_0"] = dest_dir
        config["hard_drive_0_label"] = "Workbench"

    print("prepare_dh0_files, dest_dir = ", dest_dir)

    s_dir = os.path.join(dest_dir, "S")
    # if not os.path.exists(s_dir):
    #     os.makedirs(s_dir)
    files[s_dir + os.sep] = {}
    libs_dir = os.path.join(dest_dir, "Libs")
    # if not os.path.exists(libs_dir):
    #     os.makedirs(libs_dir)
    files[libs_dir + os.sep] = {}

    devs_dir = os.path.join(dest_dir, "Devs")
    # if not os.path.exists(devs_dir):
    #     os.makedirs(devs_dir)
    files[devs_dir + os.sep] = {}
    fonts_dir = os.path.join(dest_dir, "Fonts")
    # if not os.path.exists(fonts_dir):
    #     os.makedirs(fonts_dir)
    files[fonts_dir + os.sep] = {}

    if hd_startup:
        config["hard_drive_0_priority"] = "6"
        # don't copy setpatch by default, at least not yet
        pass
    else:
        # self.hd_requirements.add("setpatch")

        # Signal to the launch system that SetPatch should be included in
        # Startup-Sequence.
        config["__setpatch__"] = "1"
        prepare_setpatch(dest_dir, files)

    workbench_version: Optional[str] = None
    amiga_model = Config(config).amiga_model()
    if amiga_model in ["A500+", "A600"]:
        workbench_version = "2.04"
    elif amiga_model.startswith("A1200"):
        workbench_version = "3.0"
    elif amiga_model.startswith("A4000"):
        workbench_version = "3.0"
    # else:
    #     workbench_version = None

    # FIXME:
    # if "workbench" in self.hd_requirements:
    #     if not workbench_version:
    #         raise Exception(
    #             "Unsupported workbench version for hd_requirements"
    #         )
    #     extractor = WorkbenchExtractor(self.fsgs)
    #     extractor.install_version(workbench_version, dest_dir)
    #     # install_workbench_files(self.fsgs, dest_dir, workbench_version)

    # for req in self.hd_requirements:
    #     if "/" in req:
    #         # assume a specific workbench file
    #         extractor = WorkbenchExtractor(self.fsgs)
    #         extractor.install_version(
    #             workbench_version,
    #             dest_dir,
    #             [req],
    #             install_startup_sequence=False,
    #         )

    if whdload_args:
        # prepare_whdload_files(dest_dir, s_dir)
        prepare_whdload_system_volume(
            dest_dir, s_dir, config=config, files=files
        )

    elif hdinst_args:
        # self.write_startup_sequence(s_dir, hdinst_args)
        raise NotImplementedError("hdinst_args needs fixing")
    elif hd_startup:
        # self.write_startup_sequence(s_dir, hd_startup)
        raise NotImplementedError("hd_startup needs fixing")

    # FIXME: Test!
    if "xpkmaster.library" in Config(config).hd_requirements():
        prepare_xpkmaster_files(dest_dir, files=files)

    system_configuration_file = os.path.join(devs_dir, "system-configuration")
    # if not os.path.exists(system_configuration_file):
    #     with open(system_configuration_file, "wb") as f:
    #         f.write(system_configuration)
    files[system_configuration_file] = {"data": system_configuration}


# def copy_setpatch(self, base_dir):
#     dest = os.path.join(base_dir, "C")
#     if not os.path.exists(dest):
#         os.makedirs(dest)
#     dest = os.path.join(dest, "SetPatch")
#     for checksum in workbench_disks_with_setpatch_39_6:
#         path = self.fsgs.file.find_by_sha1(checksum)
#         if path:
#             print("found WB DISK with SetPatch 39.6 at", path)
#             try:
#                 input_stream = self.fsgs.file.open(path)
#             except Exception:
#                 traceback.print_exc()
#             else:
#                 wb_data = input_stream.read()
#                 # archive = Archive(path)
#                 # if archive.exists(path):
#                 #     f = archive.open(path)
#                 #     wb_data = f.read()
#                 #     f.close()
#                 if self.extract_setpatch_39_6(wb_data, dest):
#                     print("SetPatch installed")
#                     self.setpatch_installed = True
#                     break
#                 else:
#                     print("WARNING: extract_setpatch_39_6 returned False")
#             # else:
#             #     print("oops, path does not exist")
#     else:
#         print("WARNING: did not find SetPatch 39.6")


# FIXME: This requires that we index .ADF files. Alternatively, we need to
# register a function instead of "data" / "sha1" in order to extract the
# SetPatch file


def prepare_setpatch(hd_dir: str, files: FilesType):
    # FIXME: Only optional if not using netplay?
    files[path.join(hd_dir, "C", "SetPatch")] = {
        "sha1": AmigaConstants.SETPATCH_39_6_SHA1,
        "optional": True,
    }


def prepare_game_hard_drive(
    config: ConfigType, drive_index, src, files: FilesType
):
    print("prepare_game_hard_drive", drive_index, src)

    if src.startswith("file_list:"):
        _scheme, dummy, drive = src.split("/")
        # file_list = config.file_list()
    else:
        _scheme, dummy, dummy, game_uuid, drive = src.split("/")
        # file_list = get_file_list_for_game_uuid(game_uuid)
        # file_list = config.file_list()
        # raise NotImplementedError("hmm")
    file_list = Config(config).file_list()

    drive_prefix = drive + "/"
    # dir_name = "DH{0}".format(drive_index)
    dir_name = drive
    # dir_path = os.path.join(self.temp_dir, dir_name)
    # dir_path = os.path.join(config.run_dir(), "HardDrives", dir_name)

    # dir_path = os.path.join("HardDrives", dir_name)
    dir_path = dir_name

    for file_entry in file_list:
        name = file_entry["name"]
        # Only process files from the correct drive
        if not name.startswith(drive_prefix):
            continue

        # extract Amiga relative path and convert each path component
        # to host file name (where needed).

        # amiga_rel_path = name[len(drive_prefix) :]
        # print("amiga_rel_path", amiga_rel_path)
        # amiga_rel_parts = amiga_rel_path.split("/")
        # for i, part in enumerate(amiga_rel_parts):
        #     # part can be blank if amiga_rel_parts is a directory
        #     # (ending with /)
        #     if part:
        #         amiga_rel_parts[i] = amiga_filename_to_host_filename(part)
        # amiga_rel_path = "/".join(amiga_rel_parts)
        amiga_rel_path = amiga_path_to_host_path(name[len(drive_prefix) :])

        dst_file = path.join(dir_path, amiga_rel_path.replace("/", os.sep))
        print(repr(dst_file))
        # x-Important to check the original name here and not the normalized path
        # x-since normalization could have changed / to \ or even remove the
        # x-trailing slash/backslash.
        # if name.endswith("/"):
        if dst_file.endswith(os.sep):
            # os.makedirs(Paths.str(dst_file))
            files[dst_file] = {}
            continue
        # if not os.path.exists(os.path.dirname(dst_file)):
        #     os.makedirs(os.path.dirname(dst_file))
        # sha1 = file_entry["sha1"]

        # current_task.set_progress(os.path.basename(dst_file))
        # current_task.set_progress(amiga_rel_path)
        # self.fsgs.file.copy_game_file("sha1://{0}".format(sha1), dst_file)
        # files.append({
        #     "path": dst_file,
        #     "sha1": file_entry["sha1"],
        #     "size": file_entry["size"]
        # })
        files[dst_file] = {
            "sha1": file_entry["sha1"],
            "size": file_entry["size"],
        }
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
            "----rwed",
            " ",
            "2000-01-01 00:00:00.00",
            " ",
            "",
            "\n",
        ]
        if "comment" in file_entry:
            metadata[4] = encode_file_comment(file_entry["comment"])
        # with open(dst_file + ".uaem", "wb") as out_file:
        #     out_file.write("".join(metadata).encode("UTF-8"))
        data = "".join(metadata).encode("UTF-8")
        files[dst_file + ".uaem"] = {
            "data": data,
            "sha1": hashlib.sha1(data).hexdigest(),
            "size": len(data),
        }

    Config(config).set_hard_drive_n(
        drive_index, os.path.join(config["run_dir"], dir_path)
    )
