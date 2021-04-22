import logging
import os
from os import path
import shutil
import traceback
from typing import BinaryIO, DefaultDict, Dict, List, Optional

from fsbc.settings import Settings
from fsgamesys.amiga.amigaconfig import AmigaConfig
from fsgamesys.amiga.config import Config
from fsgamesys.amiga.iconparser import IconParser
from fsgamesys.amiga.rommanager import ROMManager
from fsgamesys.amiga.startupsequence import prepare_startup_sequence
from fsgamesys.amiga.types import ConfigType, FilesType
from fsgamesys.archive import Archive
from fsgamesys.download import Downloader
from fsgamesys.FSGSDirectories import FSGSDirectories
from fsgamesys.options.constants import WHDLOAD_PRELOAD
from fsgamesys.options.option import Option
from fsgamesys.paths import fsgs_data_dir


def fsgs_whdload_data_dir():
    return os.path.join(fsgs_data_dir(), "WHDLoad")


def find_whdload_slave(files, hd_dir, slave_name):
    slave_name = slave_name.lower()
    hdDirWithSep = hd_dir + os.sep
    print(f"Find WHDLoad slave (lower-case name: {slave_name})")
    for path in files.keys():
        print(path)
        if not path.startswith(hdDirWithSep):
            continue
        # try:
        dirpath, filename = path.rsplit(os.sep, 1)
        # except ValueError:
        #     dirpath = ""
        #     filename = path
        if filename.lower() == slave_name:
            print("[WHDLOAD] Found", filename)
            # found_slave = True
            slave_dir = dirpath[len(hd_dir) :]
            # whdload_dir = whdload_dir.replace("\\", "/")
            if not slave_dir:
                # slave was found in root directory
                pass
            elif slave_dir[0] == os.sep:
                slave_dir = slave_dir[1:]
            return slave_dir
    return None


def prepare_whdload_system_volume(
    hd_dir, s_dir, *, config: ConfigType, files: FilesType
):
    whdload_args = Config(config).whdload_args()
    # if not whdload_args:
    #     return
    assert whdload_args

    # whdload_dir = ""
    slave_name = whdload_args.split(" ", 1)[0]
    # slave = slave_original_name.lower()
    # found_slave = False
    # # for dirpath, _dirnames, filenames in os.walk(destdir):
    # for path in files.keys():
    #     dirpath, filename = path.rsplit("/", 1)
    #     if filename.lower() == slave:
    #         print("[WHDLOAD] Found", filename)
    #         found_slave = True
    #         whdload_dir = dirpath[len(destdir) :]
    #         # whdload_dir = whdload_dir.replace("\\", "/")
    #         if not whdload_dir:
    #             # slave was found in root directory
    #             pass
    #         elif whdload_dir[0] == "/":
    #             whdload_dir = whdload_dir[1:]
    #         break
    #     if found_slave:
    #         break
    slave_dir = find_whdload_slave(files, hd_dir, slave_name)
    if slave_dir is None:
        raise Exception(
            "Did not find the specified WHDLoad slave {}. "
            "Check the WHDLoad arguments".format(repr(slave_name))
        )

    print("[WHDLOAD] Slave directory:", repr(slave_dir))
    print("[WHDLOAD] Slave arguments:", whdload_args)

    return prepare_whdload_system_volume_2(
        hd_dir,
        s_dir,
        config=config,
        slavedir=slave_dir,
        whdloadargs=whdload_args,
        files=files,
    )


def prepare_whdload_system_volume_2(
    hd_dir,
    s_dir=None,
    *,
    whdloadargs,
    slavedir,
    config: ConfigType,
    files: FilesType,
):
    if not s_dir:
        s_dir = os.path.join(hd_dir, "S")
        # if not os.path.exists(s_dir):
        #     os.makedirs(s_dir)

    # FIXME: Get whdload_args from arg
    # whdload_args = config["x_whdload_args"].strip()
    # if not whdload_args:
    #     return

    print("[WHDLOAD] prepare_whdload_system_volume_2")

    # FIXME: ...
    if config[WHDLOAD_PRELOAD] != "0":
        if " PRELOAD" not in whdloadargs.upper():
            print("[WHDLOAD] Adding PRELOAD argument")
            whdloadargs += " PRELOAD"

    # current_task.set_progress(gettext("Preparing WHDLoad..."))
    # self.on_progress(gettext("Preparing WHDLoad..."))
    print("[WHDLOAD] prepare_whdload_system_volume_2, dest_dir = ", hd_dir)

    roms_dir = hd_dir

    files[path.join(roms_dir, "Devs", "Kickstarts", "kick33180.A500")] = {
        "sha1": "11f9e62cf299f72184835b7b2a70a16333fc0d88",
        "size": 0,
    }
    files[path.join(roms_dir, "Devs", "Kickstarts", "kick34005.A500")] = {
        "sha1": "891e9a547772fe0c6c19b610baf8bc4ea7fcb785",
        "size": 0,
    }
    files[path.join(roms_dir, "Devs", "Kickstarts", "kick40068.A1200")] = {
        "sha1": "e21545723fe8374e91342617604f1b3d703094f1",
        "size": 0,
    }
    files[path.join(roms_dir, "Devs", "Kickstarts" , "kick40068.A4000")] = {
        "sha1": "5fe04842d04a489720f0f4bb0e46948199406f49",
        "size": 0,
    }

    data = prepare_prefs_file(config)
    if data is not None:
        files[path.join(s_dir, "WHDLoad.prefs")] = {"data": data}

    # FIXME
    whdload_version = Config(config).whdload_version()
    if not whdload_version:
        whdload_version = default_whdload_version

    for key, value in binaries[whdload_version].items():
        # install_whdload_file(key, hd_dir, value)
        files[path.join(hd_dir, value.replace("/", os.sep))] = {"sha1": key}
    for key, value in support_files.items():
        # install_whdload_file(key, hd_dir, value)
        files[path.join(hd_dir, value.replace("/", os.sep))] = {"sha1": key}

    if config["__netplay_game"]:
        print(
            "[WHDLOAD] Key and settings files are not copied in net play mode"
        )
    else:
        print("FIXME: Support for WHDLoad.key / WHDLoad.prefs disabled")
        # key_file = os.path.join(FSGSDirectories.get_base_dir(), "WHDLoad.key")
        # if os.path.exists(key_file):
        #     print("found WHDLoad.key at ", key_file)
        #     shutil.copy(key_file, os.path.join(s_dir, "WHDLoad.key"))
        # else:
        #     print("[WHDLOAD] Key file not found in base dir (FS-UAE dir)")

        # # Temporary feature, at least until it's possible to set more WHDLoad
        # # settings directly in the Launcher

        # prefs_file = os.path.join(
        #     FSGSDirectories.get_base_dir(), "WHDLoad.prefs"
        # )
        # if os.path.exists(prefs_file):
        #     print("found WHDLoad.prefs at ", prefs_file)
        #     shutil.copy(prefs_file, os.path.join(s_dir, "WHDLoad.prefs"))
        # else:
        #     print("[WHDLOAD] Prefs file not found in base dir (FS-UAE dir)")

    # if self.config.get("__netplay_game", ""):
    #     print("[WHDLOAD] WHDLoad base dir is not copied in net play mode")
    # else:
    #     src_dir = self.get_whdload_dir()
    #     if src_dir and os.path.exists(src_dir):
    #         print("[WHDLOAD] WHDLoad base dir exists, copying resources...")
    #         self.copy_folder_tree(src_dir, dest_dir)

    # icon = self.config.get("__whdload_icon", "")
    # icon = ""
    # if icon:
    #     shutil.copy(
    #         os.path.expanduser("~/kgiconload"),
    #         os.path.join(dest_dir, "C", "kgiconload"),
    #     )
    #     icon_path = os.path.join(dest_dir, icon)
    #     print("[WHDLOAD] Create icon at ", icon_path)
    #     create_slave_icon(icon_path, whdload_args)
    #     self.write_startup_sequence(
    #         s_dir,
    #         'cd "{0}"\n'
    #         "kgiconload {1}\n"
    #         "uae-configuration SPC_QUIT 1\n".format(
    #             whdload_dir, os.path.basename(icon)
    #         ),
    #     )
    # else:

    # FIXME: Setting setpatch to True whether found or not, currently, AmigaOS
    # will try to run this.
    setpatch = True

    data = prepare_startup_sequence(
        whdload_sequence.format(slavedir, whdloadargs), setpatch=setpatch
    )
    if data is not None:
        files[path.join(s_dir, "Startup-Sequence")] = {"data": data}


# def populate_whdload_system_volume(destdir, s_dir, *, config):
#     whdload_args = config["x_whdload_args"].strip()
#     if not whdload_args:
#         return

#     whdload_dir = ""
#     slave_original_name = whdload_args.split(" ", 1)[0]
#     slave = slave_original_name.lower()
#     found_slave = False
#     for dirpath, _dirnames, filenames in os.walk(destdir):
#         for filename in filenames:
#             if filename.lower() == slave:
#                 print("[WHDLOAD] Found", filename)
#                 found_slave = True
#                 whdload_dir = dirpath[len(destdir) :]
#                 whdload_dir = whdload_dir.replace("\\", "/")
#                 if not whdload_dir:
#                     # slave was found in root directory
#                     pass
#                 elif whdload_dir[0] == "/":
#                     whdload_dir = whdload_dir[1:]
#                 break
#         if found_slave:
#             break
#     if not found_slave:
#         raise Exception(
#             "Did not find the specified WHDLoad slave {}. "
#             "Check the WHDLoad arguments".format(repr(slave_original_name))
#         )
#     print("[WHDLOAD] Slave directory:", repr(whdload_dir))
#     print("[WHDLOAD] Slave arguments:", whdload_args)

#     return populate_whdload_system_volume_2(
#         destdir,
#         s_dir,
#         config=config,
#         slavedir=whdload_dir,
#         whdloadargs=whdload_args,
#     )


# def populate_whdload_system_volume_2(
#     destdir, s_dir=None, *, whdloadargs, slavedir, config
# ):
#     if not s_dir:
#         s_dir = os.path.join(destdir, "S")
#         if not os.path.exists(s_dir):
#             os.makedirs(s_dir)

#     # FIXME: Get whdload_args from arg
#     # whdload_args = config["x_whdload_args"].strip()
#     # if not whdload_args:
#     #     return

#     print("[WHDLOAD] LaunchHandler.copy_whdload_files")

#     # FIXME: ...
#     if config[WHDLOAD_PRELOAD] != "0":
#         if " PRELOAD" not in whdloadargs.upper():
#             print("[WHDLOAD] Adding PRELOAD argument")
#             whdloadargs += " PRELOAD"

#     # current_task.set_progress(gettext("Preparing WHDLoad..."))
#     # self.on_progress(gettext("Preparing WHDLoad..."))
#     print("[WHDLOAD] copy_whdload_files, dest_dir = ", destdir)

#     copy_whdload_kickstart(
#         destdir,
#         "kick33180.A500",
#         ["11f9e62cf299f72184835b7b2a70a16333fc0d88"],
#     )
#     copy_whdload_kickstart(
#         destdir,
#         "kick34005.A500",
#         ["891e9a547772fe0c6c19b610baf8bc4ea7fcb785"],
#     )
#     copy_whdload_kickstart(
#         destdir,
#         "kick40068.A1200",
#         ["e21545723fe8374e91342617604f1b3d703094f1"],
#     )
#     copy_whdload_kickstart(
#         destdir,
#         "kick40068.A4000",
#         ["5fe04842d04a489720f0f4bb0e46948199406f49"],
#     )

#     create_prefs_file(config, os.path.join(s_dir, "WHDLoad.prefs"))

#     # FIXME
#     whdload_version = config["x_whdload_version"]
#     if not whdload_version:
#         whdload_version = default_whdload_version

#     for key, value in binaries[whdload_version].items():
#         install_whdload_file(key, destdir, value)
#     for key, value in support_files.items():
#         install_whdload_file(key, destdir, value)

#     if config["__netplay_game"]:
#         print(
#             "[WHDLOAD] Key and settings files are not copied in net play mode"
#         )
#     else:
#         key_file = os.path.join(FSGSDirectories.get_base_dir(), "WHDLoad.key")
#         if os.path.exists(key_file):
#             print("found WHDLoad.key at ", key_file)
#             shutil.copy(key_file, os.path.join(s_dir, "WHDLoad.key"))
#         else:
#             print("[WHDLOAD] Key file not found in base dir (FS-UAE dir)")

#         # Temporary feature, at least until it's possible to set more WHDLoad
#         # settings directly in the Launcher

#         prefs_file = os.path.join(
#             FSGSDirectories.get_base_dir(), "WHDLoad.prefs"
#         )
#         if os.path.exists(prefs_file):
#             print("found WHDLoad.prefs at ", prefs_file)
#             shutil.copy(prefs_file, os.path.join(s_dir, "WHDLoad.prefs"))
#         else:
#             print("[WHDLOAD] Prefs file not found in base dir (FS-UAE dir)")

#     # if self.config.get("__netplay_game", ""):
#     #     print("[WHDLOAD] WHDLoad base dir is not copied in net play mode")
#     # else:
#     #     src_dir = self.get_whdload_dir()
#     #     if src_dir and os.path.exists(src_dir):
#     #         print("[WHDLOAD] WHDLoad base dir exists, copying resources...")
#     #         self.copy_folder_tree(src_dir, dest_dir)

#     # icon = self.config.get("__whdload_icon", "")
#     # icon = ""
#     # if icon:
#     #     shutil.copy(
#     #         os.path.expanduser("~/kgiconload"),
#     #         os.path.join(dest_dir, "C", "kgiconload"),
#     #     )
#     #     icon_path = os.path.join(dest_dir, icon)
#     #     print("[WHDLOAD] Create icon at ", icon_path)
#     #     create_slave_icon(icon_path, whdload_args)
#     #     self.write_startup_sequence(
#     #         s_dir,
#     #         'cd "{0}"\n'
#     #         "kgiconload {1}\n"
#     #         "uae-configuration SPC_QUIT 1\n".format(
#     #             whdload_dir, os.path.basename(icon)
#     #         ),
#     #     )
#     # else:
#     write_startup_sequence(
#         s_dir, whdload_sequence.format(slavedir, whdloadargs)
#     )


def install_whdload_file(sha1, dest_dir, rel_path):
    abs_path = os.path.join(dest_dir, rel_path)
    name = os.path.basename(rel_path)
    # self.on_progress(gettext("Downloading {0}...".format(name)))
    Downloader.install_file_by_sha1(sha1, name, abs_path)


from fsgamesys.FSGameSystemContext import FileContext

# def copy_whdload_kickstart(base_dir, name, checksums):
#     dest = os.path.join(base_dir, "Devs", "Kickstarts")
#     if not os.path.exists(dest):
#         os.makedirs(dest)
#     dest = os.path.join(dest, name)
#     for checksum in checksums:
#         # print("find kickstart with sha1", checksum)
#         path = FileContext.find_by_sha1(checksum)
#         if path:  # and os.path.exists(path):
#             print("found kickstart for", name, "at", path)
#             archive = Archive(path)
#             if archive.exists(path):
#                 with open(dest, "wb") as f:
#                     ROMManager.decrypt_archive_rom(archive, path, file=f)
#                 print(repr(dest))
#                 break
#             else:
#                 stream = FileContext.open(path)
#                 if stream is None:
#                     raise Exception("Cannot find kickstart " + repr(path))
#                 with open(dest, "wb") as f:
#                     f.write(stream.read())
#     else:
#         print("did not find kickstart for", name)


def should_disable_drive_click() -> bool:
    """Check if drive clicks should be disabled when generating a config."""
    return True


# def create_prefs_file(config: DefaultDict[str, str], path: str) -> bool:
#     """Write a WHDLoad.prefs respecting options from config.

#     Returns true if the prefs file was created.
#     """
#     if config[Option.NETPLAY_GAME]:
#         # The options below are commonly retrieved from settings, not
#         # config, and settings are not synced in net play, so we use
#         # default settings.
#         logging.info("[WHDLOAD] No WHDLoad overrides in net play mode")
#         return False
#     prefs = default_whdload_prefs
#     splash_delay = config[Option.WHDLOAD_SPLASH_DELAY]
#     if splash_delay:
#         prefs = prefs.replace(
#             ";SplashDelay=0", "SplashDelay={}".format(int(splash_delay))
#         )

#     quit_key = config[Option.WHDLOAD_QUIT_KEY]
#     if quit_key:
#         prefs = prefs.replace(
#             ";QuitKey=$45", "QuitKey=${}".format(quit_key.upper())
#         )

#     # Make sure the data is CRLF line terminated.
#     prefs = prefs.replace("\r\n", "\n").replace("\n", "\r\n")
#     with open(path, "wb") as f:
#         f.write(prefs.encode("ISO-8859-1"))
#     return True


def prepare_prefs_file(config: ConfigType) -> Optional[bytes]:
    """Write a WHDLoad.prefs respecting options from config.

    Returns true if the prefs file was created.
    """
    if config[Option.NETPLAY_GAME]:
        # The options below are commonly retrieved from settings, not
        # config, and settings are not synced in net play, so we use
        # default settings.
        logging.info("[WHDLOAD] No WHDLoad overrides in net play mode")
        return None
    prefs = default_whdload_prefs
    splash_delay = config[Option.WHDLOAD_SPLASH_DELAY]
    if splash_delay:
        prefs = prefs.replace(
            ";SplashDelay=0", "SplashDelay={}".format(int(splash_delay))
        )

    quit_key = config[Option.WHDLOAD_QUIT_KEY]
    if quit_key:
        prefs = prefs.replace(
            ";QuitKey=$45", "QuitKey=${}".format(quit_key.upper())
        )

    # Make sure the data is CRLF line terminated.
    prefs = prefs.replace("\r\n", "\n").replace("\n", "\r\n")
    # with open(path, "wb") as f:
    #     f.write(prefs.encode("ISO-8859-1"))
    return prefs.encode("ISO-8859-1")


def override_config(config: DefaultDict[str, str]):
    if should_disable_drive_click():
        config[Option.FLOPPY_DRIVE_VOLUME_EMPTY] = "0"
    model = Settings.instance().get(Option.WHDLOAD_MODEL)
    if model:
        if model == "A1200":
            config[Option.AMIGA_MODEL] = "A1200"
        elif model == "A1200/NONCE":
            # The following slaves do not work with A1200 non-cycle-exact
            # (non-exhaustive list, only some random tests):
            # - Cyber World
            config[Option.AMIGA_MODEL] = "A1200"
            config[Option.ACCURACY] = "0"
        config[Option.CHIP_MEMORY] = ""
        config[Option.SLOW_MEMORY] = ""
        config[Option.FAST_MEMORY] = "8192"


def read_whdload_args_from_info_data(data: bytes) -> List[str]:
    logging.debug("[WHDLOAD] Read WHDLoad args from info data")
    iconparser = IconParser(data)
    iconparser.parse()
    tooltypes = iconparser.tooltypes
    args: List[str] = []
    for tooltype in tooltypes:
        # "In a NewIcons file, one of the strings in the table (usually
        # the first one) is a single space.  The next string is the
        # message "*** DON'T EDIT THE FOLLOWING LINES!! ***". Later
        # strings contain the NewIcons data..."
        # if string == "*** DON'T EDIT THE FOLLOWING LINES!! ***":
        #     if len(args) > 1 and args == " ":
        #         args.pop()
        #     break
        if tooltype.startswith("***"):
            # Example: *** Colors ROMIcon ***
            continue
        elif tooltype.lower().startswith("slave="):
            args.insert(0, tooltype)
            # args.insert(0, tooltype[6:])
        else:
            args.append(tooltype)
    return args


def read_whdload_args_from_info_stream(stream: BinaryIO) -> List[str]:
    return read_whdload_args_from_info_data(stream.read())


def strip_whdload_slave_prefix(whdload_args: List[str]) -> List[str]:
    result = []
    for i, arg in enumerate(whdload_args):
        arg = arg.split(";")[0]
        if i == 0 and arg.lower().startswith("slave="):
            arg = arg[6:]
        if not arg.startswith("("):
            result.append(arg)
    return result


def fix_whdload_args(args: List[str]) -> str:
    """Converts args list to string and corrects args for a few icons.

    The previously performed corrections are no longer necessary. A proper icon
    parser was written.
    """
    args_str = " ".join(args)
    return args_str.strip()


def calculate_whdload_args(archive_path: str) -> str:
    """
    This function, as it is currently written, only works if there
    is an .info with the same name as the .slave file. In theory, they
    could be different since the .info file contains a slave=... tool type.
    """
    archive = Archive(archive_path)
    slave_args = {}
    lower_to_name = {}
    for path in archive.list_files():
        path_lower = path.lower()
        if path_lower.rsplit("#/", 1)[1] == "s/startup-sequence":
            logging.info(
                "[WHDLOAD] Found Startup-Sequence, assuming "
                "non-WHDLoad archive"
            )
            return ""
        lower_to_name[path_lower] = path
    for path in lower_to_name.values():
        name = os.path.basename(path)
        name_lower = name.lower()
        if name_lower.endswith(".info"):
            try:
                args = read_whdload_args_from_info_stream(archive.open(path))
                args = strip_whdload_slave_prefix(args)
            except Exception as e:
                traceback.print_exc()
                logging.warning(
                    "[WHDLOAD] WARNING: Error reading args: %s", repr(e)
                )
            else:
                if args:
                    archive_name = path.rsplit("#/", 1)[1]
                    logging.debug(
                        "[WHDLOAD] {} => {}".format(
                            archive_name, " ".join(args)
                        )
                    )
                    # EmeraldMines_v1.0_CD.lha contains \ instead of / ???
                    archive_name = archive_name.replace(
                        "EmeraldMinesCD%5c", "EmeraldMinesCD/"
                    )
                    slave_args[archive_name] = args
    if len(slave_args) == 0:
        return ""
    if len(slave_args) > 1:
        logging.debug("[WHDLOAD] Multiple WHDLoad icons found")
        # See if we have a hardcoded primary icon for this game
        for icon, args in slave_args.items():
            if icon.lower() in primary_icons:
                logging.debug("[WHDLOAD] Choosing %s as primary icon", icon)
                return fix_whdload_args(args)
        # Try to the main icon by comparing icon name to directory name
        for icon, args in slave_args.items():
            icon_lower = icon.lower()
            parts = icon_lower.split("/")
            if len(parts) == 2:
                if parts[0] + ".info" == parts[1]:
                    logging.debug(
                        "[WHDLOAD] Assuming %s as primary icon", icon
                    )
                    return fix_whdload_args(args)
        # Giving up...
        print([x.lower() for x in slave_args.keys()])
        raise Exception("Multiple icons found, couldn't decide on one")
    return fix_whdload_args(slave_args.popitem()[1])


def generate_config_for_archive(
    path: str, model_config: bool = True
) -> Dict[str, str]:
    logging.debug("[WHDLOAD] Generate config for archive %s", path)
    config = {}
    whdload_args = ""
    dummy, ext = os.path.splitext(path)
    if ext.lower() in Archive.extensions:
        try:
            whdload_args = calculate_whdload_args(path)
        except Exception:
            logging.exception("[WHDLOAD] Error while calculating WHDLoad args")
    config[Option.X_WHDLOAD_ARGS] = whdload_args
    if whdload_args and model_config:
        config[Option.AMIGA_MODEL] = "A1200"
        config[Option.FAST_MEMORY] = "8192"
        if should_disable_drive_click():
            config[Option.FLOPPY_DRIVE_VOLUME_EMPTY] = "0"
    return config


def char(v):
    return chr(v)


def write_number(f, n):
    f.write(char((n & 0xFF000000) >> 3))
    f.write(char((n & 0x00FF0000) >> 2))
    f.write(char((n & 0x0000FF00) >> 1))
    f.write(char((n & 0x000000FF) >> 0))


def write_string(f, s):
    write_number(f, len(s) + 1)
    f.write(s)
    f.write("\0")


def create_whdload_slave_icon(path, whdload_args):
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


# noinspection SpellCheckingInspection
base_icon = (
    b"\xe3\x10\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x006\x00"
    b"\x17\x00\x04\x00\x01\x00\x01\x00\x02\x1a\x98\x00\x00\x00\x00\x00"
    b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
    b"\x00\x04\x00\x00\t\x01l\x00\x01\xa5\x9c\x80\x00\x00\x00\x80\x00"
    b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x10\x00\x00\x00"
    b"\x00\x00\x006\x00\x16\x00\x02\x00\x08\xce \x03\x00\x00\x00\x00\x00"
    b"\x00\x00\x00\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00\x0c\x00"
    b"\x00\x00\x00\x00\x00\x00\x0c\x00\x00\x00\x00\x00\x00\x00\x0c\x00"
    b"\x00\x00\x00\x00\x00\x00\x0c\x00\x00\x00\x00\x00\x00\x00\x0c\x00"
    b"\x03\xf0\x0f\xff\xe0\x00\x0c\x00\x02\x080\x00\x1c\x00\x0c\x00\x02"
    b"\x07\xc0\x00\x03\x80\x0c\x00\x02\x00\x00\x00\x00`\x0c\x00\x02\x00"
    b"\x00\x00\x00\x10\x0c\x00\x02\x00\x00\x00\x00\x08\x0c\x00\x02\x07"
    b"\xc0\x00\x1f\xc4\x0c\x00\x02\x08 \x00 2\x0c\x00\x03\xf0\x18\x00"
    b"\xc0\r\x0c\x00\x00\x00\x06\x03\x00\x03\x0c\x00\x00\x00\x02\x02"
    b"\x00\x00\x0c\x00\x00\x00\x02\x02\x00\x00\x0c\x00\x00\x00\x02\x02"
    b"\x00\x00\x0c\x00\x00\x00\x03\xfe\x00\x00\x0c\x00\x00\x00\x00\x00"
    b"\x00\x00\x0c\x00\x7f\xff\xff\xff\xff\xff\xfc\x00\xff\xff\xff\xff"
    b"\xff\xff\xf8\x00\xd5UUUUUP\x00\xd5UUUUUP\x00\xd5UUUUUP\x00\xd5UUU"
    b"UUP\x00\xd5UUUUUP\x00\xd4\x05P\x00\x15UP\x00\xd4\x05@\x00\x01UP"
    b"\x00\xd4\x00\x00\x00\x00UP\x00\xd4\x00\x00\x00\x00\x15P\x00\xd4"
    b"\x00\x00\x00\x00\x05P\x00\xd4\x00\x00\x00\x00\x05P\x00\xd4\x00"
    b"\x00\x00\x00\x01P\x00\xd4\x05@\x00\x15AP\x00\xd4\x05@\x00\x15PP"
    b"\x00\xd5UP\x00UTP\x00\xd5UT\x01UUP\x00\xd5UT\x01UUP\x00\xd5UT"
    b"\x01UUP\x00\xd5UT\x01UUP\x00\xd5UUUUUP\x00\x80\x00\x00\x00\x00"
    b"\x00\x00\x00"
)

default_whdload_version = "18.5"

whdload_sequence = """
cd "{0}"
WHDLoad {1}
uae-configuration SPC_QUIT 1
"""

# noinspection SpellCheckingInspection
support_files = {
    "1d1c557f4a0f5ea88aeb96d68b09f41990340f70": "Devs/Kickstarts/kick33180.A500.RTB",
    "1ad1b55e7226bd5cd66def8370a69f19244da796": "Devs/Kickstarts/kick40068.A1200.RTB",
    "209c109855f94c935439b60950d049527d2f2484": "Devs/Kickstarts/kick34005.A500.RTB",
    "973b42dcaf8d6cb111484b3c4d3b719b15f6792d": "Devs/Kickstarts/kick40068.A4000.RTB",
    "ebf3a1f53be665bb39a636007fda3b3e640998ba": "C/uae-configuration",
    "51a37230cb45fc20fae422b8a60afd7cc8a63ed3": "C/OSEmu.400",
}
# noinspection SpellCheckingInspection
binaries = {
    "10.0": {"3096b2f41dfebf490aac015bdf0e91a80045c2c0": "C/WHDLoad"},
    "13.0": {"4bcb393e820d68b0520da9131e0d529018e303d1": "C/WHDLoad"},
    "16.0": {"883b9e37bc81fc081f78a3f278b732f97bdddf5c": "C/WHDLoad"},
    "16.1": {"250506c2444d9fb89b711b4fba5d70dd554e6f0e": "C/WHDLoad"},
    "16.2": {"a8bc2828c7da88f6236a8e82c763c71582f66cfd": "C/WHDLoad"},
    "16.3": {"5d636899fa9332b7dfccd49df3447238b5b71e49": "C/WHDLoad"},
    "16.4": {"1bb42fc83ee9237a6cfffdf15a3eb730504c9f65": "C/WHDLoad"},
    "16.5": {"8974e6c828ac18ff1cc29e56a31da0775ddeb0f0": "C/WHDLoad"},
    "16.6": {"b268bf7a05630d5b2bbf99616b32f282bac997bf": "C/WHDLoad"},
    "16.7": {"be94bc3d70d5980fac7fd04df996120e8220c1c0": "C/WHDLoad"},
    "16.8": {"a3286827c821386ac6e0bb519a7df807550d6a70": "C/WHDLoad"},
    "16.9": {"b4267a21918d6375e1bbdcaee0bc8b812e366802": "C/WHDLoad"},
    "17.0": {"0ec213a8c62beb3eb3b3509aaa44f21405929fce": "C/WHDLoad"},
    "17.1": {"1a907ca4539806b42ad5b6f7aeebacb3720e840d": "C/WHDLoad"},
    "17.2": {"d8f45f7808fb1ac356d88b8848660a6b96f04349": "C/WHDLoad"},
    "18.0": {"6f778e28673e9f931f81212ab03d9617a41cee40": "C/WHDLoad"},
    "18.1": {"fb4c64b0b5e682125e53eb2ace9bf0ccd3b8501f": "C/WHDLoad"},
    "18.2": {"0a9e7bfa1183420543e44c08410af1c5500fa704": "C/WHDLoad"},
    "18.3": {"b126b899d57f81a7646787776893416c20f43ec2": "C/WHDLoad"},
    "18.4": {"58efb174f54c67c7c48a7c1bff033c6d7a9884cb": "C/WHDLoad"},
    "18.5": {"d6b706bfbfe637bd98cd657114eea630b7d2dcc7": "C/WHDLoad"},
}
default_whdload_prefs = """
; wait for button pressed (slave must support this)
;ButtonWait

; disable cache-ability of Chip-Memory
;ChipNoCache

; path for core dump files
;CoreDumpPath=T:

; raw key code to quit with core dump (debug)
;DebugKey=$5b

; command to execute on WHDLoad startup
;ExecuteStartup=rx offline.rexx

; command to execute on WHDLoad exit
;ExecuteCleanup=rx online.rexx

; selects expert mode
;Expert

; raw key code to enter HrtMon/TK
;FreezeKey=$5d

; use MMU (for 68030)
;MMU

; ignore unwanted auto-vector interrupts
;NoAutoVec

; disable audio filter
;NoFilter

; do not flush memory
;NoFlushMem

; do not allocate memory reverse
;NoMemReverse

; disable the disk write cache
;NoWriteCache

;QuitKey=$45

; wait after reading from disk (1/50 seconds)
;ReadDelay=150

; raw key code to restart
;RestartKey=$5c

; command for Show Regs
;ShowRegs=SYS:Utilities/MuchMore W WL=80 WT=80 WW=582 WH=700

; time to display splash window (1/50 seconds)
;SplashDelay=0

; wait after saving something to disk (1/50 seconds)
;WriteDelay=150
"""
# noinspection SpellCheckingInspection
primary_icons = set(
    [
        "alchemydemo/alchemydemomine.info",
        "atrain&constrset512k/atrain512k.info",
        "atrain&constructionset/atrain.info",
        "battleisle/programm.info",
        "battleisle&datadisks/battleisle.info",
        "battleisle&datadisks/programm.info",
        # "bloodwych&extendedlevels/bloodwych.info",
        "bloodwych&extendedlevels/extendedlevels.info",
        "cadaver&cadaverthepayoff/cadaverthepayoff.info",
        "chaosstrikesback&deutil/chaosstrikesback.info",
        "chaosstrikesback&enutil/chaosstrikesback.info",
        "chaosstrikesback&frutil/chaosstrikesback.info",
        "dizzycollection/disk1.info",
        "dizzysexcellentadventures/disk1.info",
        "emeraldminescd/emeraldmine1.info",
        "epic&missiondisk/epic.info",
        "falcon&missiondisks/falcon.info",
        "falcon&missiondisksntsc/falconntsc.info",
        "goldrunner2&scenerydisks/goldrunner2.info",
        "kickoff&extratime1disk/extratime1disk.info",
        # "kickoff&extratime1disk/kickoff1disk.info",
        "kickoff&extratime2disk/extratime2disk.info",
        # "kickoff&extratime2disk/kickoff2disk.info",
        "mightandmagic3de/mightandmagic3.info",
        "pinballprelude/pinballprelude past.info",
        "pinballpreludeaga/pinballpreludeaga past.info",
        "pinballpreludeaga/past.info",
        # "populous&datadisks/populous.info",
        "populous&datadisks/finalfrontier.info",
        # "populous&datadisks/promisedlands.info",
        "populous2&challengegames/challengegames.info",
        # "populous2&challengegames/populous2.info",
        # "spacecrusade&voyagebeyond/spacecrusade.info",
        "spacecrusade&voyagebeyond/voyagebeyond.info",
        "spaceharrier&rfantasyzone/rfantasyzone.info",
        "spaceharrier&retrnfntzone/returntofantasyzone.info",
        "strippoker2+&datadisk1/datadisk1.info",
        # "strippoker2+&datadisk1/strippoker2+.info",
        "timerunnersseries/timerunners01.info",
        "utopia&newworlds/newworlds.info",
        # "utopia&newworlds/utopia.info",
        "virocop/virocop2meg.info",
        # "vroom&datadisk/datadisk.info",
        "vroom&datadisk/vroom.info",
    ]
)
