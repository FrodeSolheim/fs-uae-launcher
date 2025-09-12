from fsgs.amiga.amiga import Amiga
from fsgs.option import Option
from launcher.sync_settings import sync_settings

CONFIG_KEY_BLACKLIST = [
    "_*",
    "amigamemo_url",
    "config_feature",
    "config_name",
    "config_search",
    "configurations_dir_mtime",
    "database_arcade",
    "database_dos",
    "database_gba",
    "database_locker",
    "database_nes",
    "database_show_adult",
    "database_show_games",
    "database_snes",
    "database_url",
    "developer",
    "front_sha1",
    "hol_url",
    "irc_nick",
    "kickstarts_dir_mtime",
    "languages",
    "last_cd_dir",
    "last_floppy_dir",
    "last_hd_dir",
    "last_rom_dir",
    "last_scan",
    "last_settings_page",
    Option.LAUNCHER_THEME,
    "lemon_url",
    "mobygames_url",
    "netplay_feature",
    "parent_uuid",
    "platform",
    "players",
    "primary_joystick",
    "publisher",
    "screen1_sha1",
    "screen2_sha1",
    "screen3_sha1",
    "screen4_sha1",
    "screen5_sha1",
    "search_path",
    "title_sha1",
    "variant_rating",
    "variant_uuid",
    "whdload_url",
    "wikipedia_url",
    "x_*",
    "year",
]


class ConfigWriter(object):
    def __init__(self, config):
        self.config = config

    def create_fsuae_config(self):
        print("create_fsuae_config")
        c = []

        num_drives = 0
        for i in range(sync_settings.MAX_FLOPPY_DRIVES):
            key = "floppy_drive_{0}".format(i)
            value = self.config.get(key)
            if value:
                num_drives = i + 1
        num_drives = max(1, num_drives)

        print("")
        print("-------------" * 6)
        print("CONFIG")
        c.append("[fs-uae]")
        for key in sorted(self.config.keys()):
            ignore = False
            if key.startswith("floppy_drive_"):
                for i in range(4):
                    if key == "floppy_drive_{0}".format(i):
                        if i >= num_drives:
                            ignore = True
                            break
            normalized_key = key.lower().replace("-", "_")
            for ignore_key in CONFIG_KEY_BLACKLIST:
                if ignore_key == normalized_key or (
                    ignore_key.endswith("*")
                    and normalized_key.startswith(ignore_key[:-1])
                ):
                    ignore = True
            if ignore:
                continue
            value = self.config[key]
            print(key, repr(value))
            value = value.replace("\\", "\\\\")
            if value:
                c.append("{0} = {1}".format(key, value))

        return c
