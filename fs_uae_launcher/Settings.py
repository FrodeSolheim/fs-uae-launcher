from fsbc.Application import app
from fsbc.user import get_user_name
from .Signal import Signal


class Settings(object):
    irc_server = "irc.fengestad.no"

    base_dir = ""

    # The main use of default_settings is actually to hide the corresponding
    # options from advanced settings (because there is UI for them, or
    # because the settings are internal)
    default_settings = {
        "__netplay_ready": "",
        "automatic_input_grab": "",
        "audio_frequency": "",
        "audio_buffer_target_size": "",
        "builtin_configs": "",
        "config_base": "",
        "config_changed": "0",
        "config_name": "Unnamed Configuration",
        "config_feature": "",
        "config_path": "",
        "config_refresh": "",
        "config_search": "",
        "config_xml_path": "",
        "configurations_dir_mtime": "",
        "database_auth": "",
        "database_email": "",
        "database_feature": "",
        "database_password": "",
        "database_server": "",
        "database_show_adult": "",
        "database_show_games": "",
        "database_username": "",
        "device_id": "",
        "fsaa": "",
        "floppy_drive_volume": "",
        "floppy_drive_volume_empty": "",
        "fullscreen": "",
        "game_uuid": "",
        "game_list_uuid": "",
        "initial_input_grab": "",
        "irc_nick": "",
        "irc_server": "",
        "keep_aspect": "",
        "kickstarts_dir_mtime": "",
        "kickstart_setup": "",
        "language": "",
        "last_cd_dir": "",
        "last_floppy_dir": "",
        "last_hd_dir": "",
        "last_rom_dir": "",
        "last_scan": "",
        "last_settings_page": "",
        "launcher_theme": "",
        "low_latency_vsync": "",
        "maximized": "0",
        "middle_click_ungrab": "",
        "monitor": "",
        "mouse_speed": "",
        "netplay_feature": "",
        "netplay_tag": "",
        "parent_uuid": "",
        "primary_joystick": "",
        # "rtg_scanlines": "",
        "scan_configs": "1",
        "scan_files": "1",
        "scan_roms": "1",
        # "scanlines": "",
        "search_path": "",
        "secondary_joystick": "",
        "stereo_separation": "",
        "swap_ctrl_keys": "",
        "texture_filter": "",
        "texture_format": "",
        "video_format": "",
        "video_sync": "",
        "video_sync_method": "",
        "zoom": "",
        # "window_width": "",
        # "window_height": "",
    }

    settings = default_settings.copy()
    # settings_listeners = []

    initialize_from_config = set([
        "fullscreen",
    ])

    @classmethod
    def get(cls, key):
        return app.settings[key]

    @classmethod
    def set(cls, key, value):
        app.settings[key] = value

    @classmethod
    def add_listener(cls, listener):
        # cls.settings_listeners.append(listener)
        Signal.add_listener("setting", listener)

    @classmethod
    def remove_listener(cls, listener):
        # cls.settings_listeners.remove(listener)
        Signal.remove_listener("setting", listener)

    @classmethod
    def get_irc_nick(cls):
        value = cls.get("irc_nick").strip()
        if not value:
            value = get_user_name()
        # these are probably valid too: \`
        valid_chars = ("ABCDEFGHIJKLMNOPQRSTUVWXYZ"
                       "abcdefghijklmnopqrstuvwxyz"
                       "_[]{}|^")
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
        return "irc.fengestad.no"
