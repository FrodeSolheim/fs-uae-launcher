# FIXME: send fsgs as parameter to ValueConfigLoader instead
from fsgs.context import fsgs
import os
import json
from fsbc.paths import Paths
from fsgs.amiga.amiga import Amiga
from fsgs.filedatabase import FileDatabase
from fsgs.network import openretro_url_prefix
from fsgs.option import Option
from fsgs.amiga import whdload


class ValueConfigLoader(object):
    DB_VERSION_MAX = 1

    def __init__(self, uuid=""):
        self.config = {}
        self.options = {}
        self.viewport = []
        self.values = {}
        self.uuid = uuid
        self._file_list = None
        self._cue_sheets = None
        if uuid:
            self.options["database_url"] = "{0}/game/{1}".format(
                openretro_url_prefix(), uuid
            )

    def get_config(self):
        return self.config.copy()

    def load_values(self, values):
        if values.get("db_version"):
            try:
                version = int(values.get("db_version"))
            except ValueError:
                version = 10000
            if version > self.DB_VERSION_MAX:
                self.config["__config_name"] = (
                    "Unsupported Database "
                    "Version (Please upgrade FS-UAE Launcher)"
                )
                return self.get_config()

        self.values = values
        # from pprint import pprint
        # pprint(values)

        cd_based = False
        amiga_model = "A500"
        platform = self.values.get("platform", "Amiga")
        self.options["platform"] = platform.lower()

        platform = platform.lower()
        if platform == "amiga":
            pass
        elif platform == "cd32":
            amiga_model = "CD32"
            cd_based = True
            self.options["joystick_port_1_mode"] = "cd32 gamepad"
        elif platform == "cdtv":
            amiga_model = "CDTV"
            cd_based = True
        else:
            raise Exception("unknown platform")
        self.config["amiga_model"] = amiga_model

        # self.config["x_game_uuid"] = self.values["uuid"]

        self.viewport = []
        # game_node = self.root.find("game")
        # if game_node is not None:
        #     game_uuid = game_node.get("uuid", "")
        #     self.config["x_game_uuid"] = game_uuid
        #     self.load_game_info(game_uuid)

        # self.load_options())

        sort_list = []
        for key in values:
            if key == "chip_memory":
                # chip memory is checked at the end because of support for
                # the 1024+ value, and others keys can change amiga_model..
                sort_list.append(("x_chip_memory", key))
            else:
                sort_list.append((key, key))
        sort_list.sort()

        for dummy, key in sort_list:
            self.load_option(key, values[key])

        if self.viewport:
            self.options["viewport"] = ", ".join(self.viewport)

        if cd_based:
            if self.check_all_files():
                self.load_cdroms()
        else:
            self.load_floppies()

        self.load_hard_drives()

        # if not self.check_all_files():
        #     print(" -- some files are missing --")
        #     self.options["x_missing_files"] = "1"

        download_page = values.get("download_page", "")
        if download_page:
            self.options["download_page"] = download_page
        download_file = values.get("download_file", "")
        if download_file:
            self.options["download_file"] = download_file
        download_terms = values.get("download_terms", "")
        if download_terms:
            self.options["download_terms"] = download_terms
        download_notice = values.get("download_notice", "")
        if download_notice:
            self.options["download_notice"] = download_notice

        # for now, just copy all options to config without checking
        for key, value in self.options.items():
            self.config[key] = value

        if self.config.get(Option.X_WHDLOAD_ARGS):
            whdload.override_config(self.config)

        if (
            self.config.get("amiga_model", "") == "A500"
            and self.config.get("slow_memory") == "0"
        ):
            self.config["amiga_model"] = "A500/512K"
            self.config["slow_memory"] = ""

        self.set_name_and_uuid()
        self.contract_paths()
        return self.get_config()

    def check_all_files(self):
        file_list_json = self.values.get("file_list", "[]")
        file_list = json.loads(file_list_json)
        for file in file_list:
            if file["name"].endswith("/"):
                # this is a folder
                continue
            # print(repr(file))
            if not file["sha1"]:
                return False
            if not fsgs.file.find_by_sha1(file["sha1"]):
                return False
        return True

    def contract_paths(self):
        def fix(key):
            if self.config.get(key):
                self.config[key] = Paths.contract_path(
                    self.config.get(key), default_dir, force_real_case=False
                )

        default_dir = fsgs.amiga.get_floppies_dir()
        for i in range(Amiga.MAX_FLOPPY_DRIVES):
            fix("floppy_drive_{0}".format(i))
        for i in range(Amiga.MAX_FLOPPY_IMAGES):
            fix("floppy_image_{0}".format(i))

        default_dir = fsgs.amiga.get_cdroms_dir()
        for i in range(Amiga.MAX_CDROM_DRIVES):
            fix("cdrom_drive_{0}".format(i))
        for i in range(Amiga.MAX_CDROM_IMAGES):
            fix("cdrom_image_{0}".format(i))

    def set_name_and_uuid(self):
        # self.config["x_config_uuid"] = self.root.get("uuid", "")

        self.config["game_uuid"] = self.values.get("game_uuid", "")
        self.config["variant_uuid"] = self.values.get("variant_uuid", "")

        game_name = self.values.get("game_name", "")
        platform_name = self.values.get("platform", "")
        variant_name = self.values.get("variant_name", "")
        parts = []
        if platform_name:
            parts.append(platform_name)
        if variant_name:
            parts.append(variant_name)
        if game_name and variant_name:
            config_name = "{0} ({1})".format(game_name, ", ".join(parts))
            self.config["__config_name"] = config_name
        else:
            self.config["__config_name"] = self.values.get("config_name", "")

    def load_option(self, key, value):
        model = self.options.get("amiga_model", "")
        if key in ["variant_viewport", "viewport"]:
            if "=" in value:
                parts = value.split(",")
                for i in range(len(parts)):
                    parts[i] = parts[i].split("#", 1)[0].strip()
                    # parts[i] = parts[i].replace("=", "=>")
                    # parts[i] = parts[i].replace("==>", "=>")
                value = ", ".join(parts)
                while "  " in value:
                    value = value.replace("  ", " ")
            else:
                value = "* * * * = " + value
            self.viewport.append(value)
        # if key.startswith("viewport_"):
        #     parts = key.split("_")
        #     if len(parts) == 5:
        #         parts = parts[1:]
        #         value = " ".join(parts) + " => " + value
        #         value = value.replace("x", "*")
        #         self.viewport.append(value)
        elif key == "hd_startup":
            self.options["hd_startup"] = value
            if whdload.should_disable_drive_click():
                self.options[Option.FLOPPY_DRIVE_VOLUME_EMPTY] = "0"
        elif key == "whdload_args":
            self.options[Option.X_WHDLOAD_ARGS] = value
        elif key == "whdload_quit_key":
            self.options[Option.WHDLOAD_QUIT_KEY] = value
        elif key == "hdinst_args":
            self.options["x_hdinst_args"] = value
            if whdload.should_disable_drive_click():
                self.options[Option.FLOPPY_DRIVE_VOLUME_EMPTY] = "0"
        elif key == "hd_requirements":
            self.options["hd_requirements"] = value
        elif key == "save_disk":
            self.options["save_disk"] = value
        elif key == "whdload_version":
            self.options["x_whdload_version"] = value
        # elif key == "whdload_icon":
        #     self.options["__whdload_icon"] = value
        elif key == "kickstart":
            if value == "1.2":
                self.options["amiga_model"] = "A1000"
            elif value == "2.0":
                if model in ["A500+", "A600"]:
                    pass
                else:
                    self.options["amiga_model"] = "A600"
            elif value == "2.0+":
                if model in [
                    "A500+",
                    "A600",
                    "A1200",
                    "A1200/020",
                    "A3000",
                    "A4000/040",
                ]:
                    pass
                else:
                    self.options["amiga_model"] = "A600"
            elif value in ["3.0+", "3.1", "3.1+"]:
                if model in ["A1200", "A1200/020", "A3000", "A4000/040"]:
                    pass
                else:
                    self.options["amiga_model"] = "A1200"
            elif value == "AROS":
                self.options["kickstart_file"] = "internal"
            else:
                # FIXME: print warning
                pass
        elif key == "chipset":
            if value == "ECS":
                if model in ["A500+", "A600", "A3000"]:
                    pass
                else:
                    self.options["amiga_model"] = "A600"
            elif value == "AGA":
                if model in ["A1200", "A1200/020", "A4000/040"]:
                    pass
                else:
                    self.options["amiga_model"] = "A1200"
        elif key == "cpu":
            if value == "68020+" or value == "68020":
                if model in ["A1200", "A1200/020", "A3000", "A4000/040"]:
                    pass
                else:
                    self.options["amiga_model"] = "A1200"
        elif key == "fast_memory":
            ivalue = int(value)
            if ivalue > 8192:
                self.options["zorro_iii_memory"] = value
                self.options["amiga_model"] = "A1200/020"
            else:
                self.options["fast_memory"] = value
        elif key == "chip_memory":
            model = self.options.get("amiga_model", "")
            if value == "1024+":
                if model in ["A1200", "A1200/020", "A4000/040"]:
                    pass
                else:
                    self.options["chip_memory"] = "1024"
            elif value == "2048+":
                if model in ["A1200", "A1200/020", "A4000/040"]:
                    pass
                else:
                    # self.options["amiga_model"] = "A1200"
                    self.options["chip_memory"] = "2048"
            else:
                self.options["chip_memory"] = value
        elif key == "video_standard":
            if value == "NTSC":
                self.options["ntsc_mode"] = "1"
        elif key == "cracktro":
            # FIXME: handle
            pass
        elif key in [
            "joystick_port_0_mode",
            "joystick_port_1_mode",
            "joystick_port_2_mode",
            "joystick_port_3_mode",
            "joystick_port_4_mode",
        ]:
            self.load_joystick_port_x_mode_option(key, value)
        elif key in [
            "amiga_model",
            "accuracy",
            "cdrom_drive_0_delay",
            "floppy_drive_count",
            "slow_memory",
            "front_sha1",
            "screen1_sha1",
            "screen2_sha1",
            "screen3_sha1",
            "screen4_sha1",
            "screen5_sha1",
            "title_sha1",
            "year",
            "publisher",
            "developer",
            "hol_url",
            "lemon_url",
            "wikipedia_url",
            "mobygames_url",
            "whdload_url",
            "amigamemo_url",
            "longplay_url",
            "thelegacy_url",
            "homepage_url",
            "languages",
            "dongle_type",
        ]:
            self.options[key] = value
        elif key == "requirements":
            if "wb" in value.lower():
                self.options["hard_drive_0"] = "hd://template/workbench/DH0"
                self.options["hard_drive_0_priority"] = "6"
            elif "hd" in value.lower():
                self.options["hard_drive_0"] = "hd://template/empty/DH0"
        elif key == "players":
            self.options["players"] = value
        elif key == "protection":
            self.options["protection"] = value
        elif key == "game_notice":
            self.options["x_game_notice"] = value
        elif key == "variant_notice":
            self.options["x_variant_notice"] = value
        elif key == "variant_warning":
            self.options["x_variant_warning"] = value
        elif key == "variant_error":
            self.options["x_variant_error"] = value
        elif key == "joy_emu_conflict":
            self.options["x_joy_emu_conflict"] = value
            # elif key == "languages":
            #     self.options["x_languages"] = value

    def load_joystick_port_x_mode_option(self, key, value):
        value = value.lower()
        if "," not in value:
            self.options[key] = value
            return
        parts = value.split(",")
        assert "=" not in parts[0]
        self.options[key] = parts[0]
        port = ["0", "1", "2", "3", "4"].index(key[14])
        for part in parts[1:]:
            k, v = part.split("=")
            k = k.strip()
            v = v.strip()
            if not v.startswith("action_"):
                v = "action_" + v
            k = "joystick_port_{0}_{1}".format(port, k)
            self.options[k] = v

    def get_file_list(self):
        if self._file_list is None:
            file_list_json = self.values.get("file_list", "[]")
            self._file_list = json.loads(file_list_json)
        return self._file_list

    def get_cue_sheets(self):
        if self._cue_sheets is None:
            cue_sheets_json = self.values.get("cue_sheets", "[]")
            self._cue_sheets = json.loads(cue_sheets_json)
        return self._cue_sheets

    def build_media_list(self, floppies=False, cds=False, hds=False):
        media_list = []
        added = set()
        for file_item in self.get_file_list():
            name = file_item["name"]
            url = file_item.get("url", "")

            if name.startswith("DH0/"):
                if hds:
                    # p = os.path.join(self.path, "HardDrive")
                    p = "hd://game/" + self.uuid + "/DH0"
                    if p in added:
                        # already added
                        continue
                    added.add(p)
                    # FIXME: hack for now
                    sha1 = self.values.get("dh0_sha1", "")
                    media_list.append((p, sha1))
                else:
                    continue

            sha1 = file_item["sha1"]
            base, ext = os.path.splitext(name)
            ext = ext.lower()

            if hds:
                if ext not in [".zip"]:
                    continue
            elif cds:
                if ext not in [".cue", ".iso"]:
                    continue
                if "(Track" in base:
                    # probably part of a split multi-track cue
                    continue
            elif floppies:
                if ext not in [".adf", ".adz", ".dms", ".ipf"]:
                    continue

            path = ""
            found_sha1 = ""
            if sha1:
                print(sha1)
                file = FileDatabase.get_instance().find_file(sha1=sha1)
                if file:
                    found_sha1 = sha1
                    path = file["path"]
            if url and not path:
                path = url
                found_sha1 = sha1

            if path:
                media_list.append((path, found_sha1))
            else:
                pass
                # return False
                #  FIXME: handle it with a visible error message
                # raise Exception("could not find file " + repr(name))
        return media_list

    def load_floppies_from_floppy_list(self):
        media_list = []
        for item in self.values.get("floppy_list").split(","):
            name, sha1 = item.split(":")
            name = name.strip()
            sha1 = sha1.strip()
            path = "sha1://{0}/{1}/{2}".format(sha1, "", name)
            media_list.append((path, sha1))
        return media_list

    def load_floppies(self):
        floppy_drive_count = 4
        if "floppy_drive_count" in self.options:
            try:
                floppy_drive_count = int(self.options["floppy_drive_count"])
            except ValueError:
                floppy_drive_count = 1
            floppy_drive_count = max(0, min(4, floppy_drive_count))

        if self.values.get("floppy_list", ""):
            media_list = self.load_floppies_from_floppy_list()
        else:
            media_list = self.build_media_list(floppies=True)

        for i, values in enumerate(media_list):
            path, sha1 = values
            if i < floppy_drive_count:
                self.config["floppy_drive_{0}".format(i)] = path
                self.config["x_floppy_drive_{0}_sha1".format(i)] = sha1
            self.config["floppy_image_{0}".format(i)] = path
            self.config["x_floppy_image_{0}_sha1".format(i)] = sha1
        if floppy_drive_count < 4:
            self.config["floppy_drive_count"] = floppy_drive_count

    def cdrom_sha1_to_uri(self, sha1):
        for file_item in self.get_file_list():
            if file_item["sha1"] == sha1:
                return "game://{}/{}".format(self.uuid, file_item["name"])
        raise Exception("cdrom_sha1_to_uri: could not find " + sha1)

    def load_cdroms(self):
        # media_list = self.build_media_list(cds=True)
        cue_sheets = self.get_cue_sheets()
        if cue_sheets:
            return self.load_cdroms_from_cue_sheets(cue_sheets)
        cue = False
        ccd = False
        # iso = False
        for file_item in self.get_file_list():
            if file_item["name"].endswith(".cue"):
                cue = True
            if file_item["name"].endswith(".ccd"):
                ccd = True
                # if file_item["name"].endswith(".iso"):
                #     iso = True
        media_list = []
        if ccd:
            ext = ".ccd"
        elif cue:
            ext = ".cue"
        else:
            ext = ".iso"
        for file_item in self.get_file_list():
            if file_item["name"].endswith(ext):
                media_list.append((file_item["name"], file_item["sha1"]))
        print("load_cdroms media_list =", media_list)
        for i, values in enumerate(media_list):
            path, sha1 = values
            path = self.cdrom_sha1_to_uri(sha1)
            if i < 1:
                self.config["cdrom_drive_{0}".format(i)] = path
                self.config["x_cdrom_drive_{0}_sha1".format(i)] = sha1
            self.config["cdrom_image_{0}".format(i)] = path
            self.config["x_cdrom_image_{0}_sha1".format(i)] = sha1

    def load_cdroms_from_cue_sheets(self, cue_sheets):
        for i, item in enumerate(cue_sheets):
            path = "game://{}/{}".format(self.uuid, item["name"])
            if i < 1:
                self.config["cdrom_drive_{0}".format(i)] = path
            self.config["cdrom_image_{0}".format(i)] = path

    def load_hard_drives(self):
        media_list = self.build_media_list(hds=True)
        print(media_list)
        for i, values in enumerate(media_list):
            path, sha1 = values
            self.config["hard_drive_{0}".format(i)] = path
            self.config["x_hard_drive_{0}_sha1".format(i)] = sha1
