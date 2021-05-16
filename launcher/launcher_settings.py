from fsbc.settings import Settings
from fsbc.user import get_user_name
from launcher.option import Option

from .launcher_signal import LauncherSignal


class LauncherSettings(object):
    base_dir = ""

    # These are not used any more, and should be removed from settings if
    # found.
    old_keys = {"config_base", "config_refresh"}

    # The main use of default_settings is actually to hide the corresponding
    # options from advanced settings (because there is UI for them, or
    # because the settings are internal)
    default_settings = {
        "__netplay_ready": "",
        "__config_refresh": "",
        "automatic_input_grab": "",
        Option.ARCADE_DATABASE: "",
        "arcade_fullscreen": "",
        "audio_frequency": "",
        "audio_buffer_target_size": "",
        "builtin_configs": "",
        Option.C64_DATABASE: "",
        "config_changed": "0",
        "config_name": "Unnamed Configuration",
        "config_feature": "",
        "config_path": "",
        Option.CPC_DATABASE: "",
        "config_search": "",
        "configurations_dir_mtime": "",
        "database_auth": "",
        "database_email": "",
        "database_feature": "",
        "database_password": "",
        "database_server": "",
        Option.DATABASE_SHOW_ADULT: "",
        Option.DATABASE_SHOW_GAMES: "",
        Option.DATABASE_SHOW_UNPUBLISHED: "",
        "database_username": "",
        "device_id": "",
        Option.DOS_DATABASE: "",
        "fsaa": "",
        "floppy_drive_volume": "",
        Option.FLOPPY_DRIVE_VOLUME_EMPTY: "",
        "fullscreen": "",
        "game_uuid": "",
        "game_list_uuid": "",
        Option.GB_DATABASE: "",
        Option.GBA_DATABASE: "",
        Option.GBC_DATABASE: "",
        "initial_input_grab": "",
        "irc_nick": "",
        "irc_server": "",
        "keep_aspect": "",
        "kickstarts_dir_mtime": "",
        "kickstart_setup": "",
        "language": "",
        "last_cartridge_dir": "",
        "last_cd_dir": "",
        "last_floppy_dir": "",
        "last_hd_dir": "",
        "last_rom_dir": "",
        "last_scan": "",
        "last_tape_dir": "",
        "last_settings_page": "",
        Option.LAUNCHER_CLOSE_BUTTONS: "",
        Option.LAUNCHER_THEME: "",
        "low_latency_vsync": "",
        "maximized": "0",
        "middle_click_ungrab": "",
        "monitor": "",
        "mouse_speed": "",
        Option.NEOGEO_DATABASE: "",
        Option.NES_DATABASE: "",
        "netplay_feature": "1",
        "netplay_tag": "",
        "parent_uuid": "",
        Option.PLATFORMS_FEATURE: "",
        "primary_joystick": "",
        Option.PSX_DATABASE: "",
        # "rtg_scanlines": "",
        "scan_configs": "1",
        "scan_files": "1",
        "scan_roms": "1",
        # "scanlines": "",
        "search_path": "",
        "secondary_joystick": "",
        Option.SMD_DATABASE: "",
        Option.SMD_EMULATOR: "",
        Option.SMS_DATABASE: "",
        Option.SNES_DATABASE: "",
        Option.ST_DATABASE: "",
        "stereo_separation": "",
        "swap_ctrl_keys": "",
        "texture_filter": "",
        "texture_format": "",
        Option.TG16_DATABASE: "",
        Option.TGCD_DATABASE: "",
        "__variant_rating": "",
        "video_format": "",
        "video_sync": "",
        "video_sync_method": "",
        Option.WHDLOAD_PRELOAD: "",
        Option.WHDLOAD_SPLASH_DELAY: "",
        Option.WHDLOAD_QUIT_KEY: "",
        # "window_width": "",
        # "window_height": "",
        "zoom": "",
        Option.ZXS_DATABASE: "",
    }

    settings = default_settings.copy()
    # settings_listeners = []

    initialize_from_config = {"fullscreen"}

    @classmethod
    def get(cls, key: str):
        # return app.settings.get(key, cls.default_settings.get(key, ""))
        return Settings.instance().get(key)

    @classmethod
    def set(cls, key: str, value: str):
        Settings.instance()[key] = value

    @classmethod
    def keys(cls):
        return Settings.instance().values.keys()

    @classmethod
    def items(cls):
        return Settings.instance().values.items()

    @classmethod
    def add_listener(cls, listener):
        # cls.settings_listeners.append(listener)
        LauncherSignal.add_listener("setting", listener)

    @classmethod
    def remove_listener(cls, listener):
        # cls.settings_listeners.remove(listener)
        LauncherSignal.remove_listener("setting", listener)

    @classmethod
    def get_irc_nick(cls):
        value = cls.get("irc_nick").strip()
        if not value:
            value = get_user_name()
        # these are probably valid too: \`
        valid_chars = (
            "ABCDEFGHIJKLMNOPQRSTUVWXYZ" "abcdefghijklmnopqrstuvwxyz" "_[]{}|^"
        )
        extra_valid_chars = "0123456789-"
        nick = ""
        for c in value:
            if c in valid_chars:
                nick = nick + c
                if extra_valid_chars:
                    valid_chars += extra_valid_chars
                    extra_valid_chars = ""
        if not nick:
            nick = "User"
        return nick

    @classmethod
    def get_irc_nickserv_pass(cls):
        value = cls.get("irc_nickserv_pass").strip()
        if value:
            return value
        return ""

    @classmethod
    def get_irc_server(cls):
        value = cls.get("irc_server").strip()
        if value:
            return value
        return "irc.fs-uae.net"
