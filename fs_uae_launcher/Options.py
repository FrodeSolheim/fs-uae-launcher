# Automatically generated - do not edit by hand


class Option(object):
    """Constants for option names."""    
    ACCELERATOR = "accelerator"
    ACCELERATOR_MEMORY = "accelerator_memory"
    AUDIO_BUFFER_TARGET_BYTES = "audio_buffer_target_bytes"
    AUDIO_BUFFER_TARGET_SIZE = "audio_buffer_target_size"
    AUDIO_FREQUENCY = "audio_frequency"
    AUTOMATIC_INPUT_GRAB = "automatic_input_grab"
    BLIZZARD_SCSI_KIT = "blizzard_scsi_kit"
    BSDSOCKET_LIBRARY = "bsdsocket_library"
    BUILTIN_CONFIGS = "builtin_configs"
    CDROM_DRIVE_COUNT = "cdrom_drive_count"
    CHIP_MEMORY = "chip_memory"
    CONFIG_FEATURE = "config_feature"
    CPU = "cpu"
    CPU_IDLE = "cpu_idle"
    DATABASE_ARCADE = "database_arcade"
    DATABASE_AUTH = "database_auth"
    DATABASE_DOS = "database_dos"
    DATABASE_EMAIL = "database_email"
    DATABASE_FEATURE = "database_feature"
    DATABASE_GBA = "database_gba"
    DATABASE_LOCKER = "database_locker"
    DATABASE_NES = "database_nes"
    DATABASE_PASSWORD = "database_password"
    DATABASE_SERVER = "database_server"
    DATABASE_SHOW_ADULT = "database_show_adult"
    DATABASE_SHOW_GAMES = "database_show_games"
    DATABASE_SNES = "database_snes"
    DATABASE_USERNAME = "database_username"
    DEVICE_ID = "device_id"
    DONGLE_TYPE = "dongle_type"
    FADE_IN_DURATION = "fade_in_duration"
    FLOPPY_DRIVE_COUNT = "floppy_drive_count"
    FLOPPY_DRIVE_SPEED = "floppy_drive_speed"
    FLOPPY_DRIVE_VOLUME = "floppy_drive_volume"
    FLOPPY_DRIVE_VOLUME_EMPTY = "floppy_drive_volume_empty"
    FSAA = "fsaa"
    FULLSCREEN = "fullscreen"
    GRAPHICS_CARD = "graphics_card"
    GRAPHICS_MEMORY = "graphics_memory"
    INITIAL_INPUT_GRAB = "initial_input_grab"
    IRC_NICK = "irc_nick"
    IRC_SERVER = "irc_server"
    KEEP_ASPECT = "keep_aspect"
    KEYBOARD_INPUT_GRAB = "keyboard_input_grab"
    KEYBOARD_KEY_BACKSLASH = "keyboard_key_backslash"
    KEYBOARD_KEY_EQUALS = "keyboard_key_equals"
    KEYBOARD_KEY_INSERT = "keyboard_key_insert"
    KEYBOARD_KEY_LESS = "keyboard_key_less"
    KICKSTART_SETUP = "kickstart_setup"
    LAUNCHER_THEME = "launcher_theme"
    LOAD_STATE = "load_state"
    LOG_AUTOSCALE = "log_autoscale"
    LOG_INPUT = "log_input"
    LOG_QUERY_PLANS = "log_query_plans"
    LOW_LATENCY_VSYNC = "low_latency_vsync"
    MIDDLE_CLICK_UNGRAB = "middle_click_ungrab"
    MIN_FIRST_LINE_NTSC = "min_first_line_ntsc"
    MIN_FIRST_LINE_PAL = "min_first_line_pal"
    MONITOR = "monitor"
    MOUSE_SPEED = "mouse_speed"
    NETPLAY_FEATURE = "netplay_feature"
    NETPLAY_TAG = "netplay_tag"
    RTG_SCANLINES = "rtg_scanlines"
    SCANLINES = "scanlines"
    SOUND_CARD = "sound_card"
    STEREO_SEPARATION = "stereo_separation"
    SWAP_CTRL_KEYS = "swap_ctrl_keys"
    TEXTURE_FILTER = "texture_filter"
    TEXTURE_FORMAT = "texture_format"
    UAE_A2065 = "uae_a2065"
    UAE_A3000MEM_SIZE = "uae_a3000mem_size"
    UAE_CHIPSET_COMPATIBLE = "uae_chipset_compatible"
    UAE_CPU_FREQUENCY = "uae_cpu_frequency"
    UAE_CPU_MULTIPLIER = "uae_cpu_multiplier"
    UAE_CPU_SPEED = "uae_cpu_speed"
    UAE_CPU_THROTTLE = "uae_cpu_throttle"
    UAE_FASTMEM2_SIZE = "uae_fastmem2_size"
    UAE_FASTMEM_AUTOCONFIG = "uae_fastmem_autoconfig"
    UAE_FASTMEM_SIZE = "uae_fastmem_size"
    UAE_FORCE_0X10000000_Z3 = "uae_force_0x10000000_z3"
    UAE_GFX_LINEMODE = "uae_gfx_linemode"
    UAE_MBRESMEM_SIZE = "uae_mbresmem_size"
    UAE_RTC = "uae_rtc"
    UAE_SANA2 = "uae_sana2"
    UAE_SLIRP_IMPLEMENTATION = "uae_slirp_implementation"
    UAE_SOUND_OUTPUT = "uae_sound_output"
    UAE_TOCCATA = "uae_toccata"
    UAE_Z3CHIPMEM_SIZE = "uae_z3chipmem_size"
    UAE_Z3MAPPING = "uae_z3mapping"
    UAE_Z3MEM2_SIZE = "uae_z3mem2_size"
    UAE_Z3MEM_SIZE = "uae_z3mem_size"
    UAEGFX_CARD = "uaegfx_card"
    UAEM_WRITE_FLAGS = "uaem_write_flags"
    VIDEO_FORMAT = "video_format"
    VIDEO_SYNC = "video_sync"
    VIDEO_SYNC_METHOD = "video_sync_method"
    VOLUME = "volume"
    WHDLOAD_SPLASH_DELAY = "whdload_splash_delay"
    WINDOW_BORDER = "window_border"
    ZOOM = "zoom"


class Options(object):

    @staticmethod
    def get(name):
        return options[name]


N_ = lambda x: x


options = {

    "accelerator": {
        "default": "0",
        "description": N_("CPU Accelerator Board"),
        "type": "Choice",
        "values": [
            ("0", N_("None")),
            ("blizzard-1230-iv", "Blizzard 1230 IV"),
            ("blizzard-1240", "Blizzard 1240"),
            ("blizzard-1260", "Blizzard 1260"),
            ("blizzard-ppc", "Blizzard PPC"),
            ("cyberstorm-ppc", "CyberStorm PPC"),
        ]
    },

    "accelerator_memory": {
        "default": "",
        "description": N_("CPU Accelerator Board RAM"),
        "type": "Choice",
        "values": [
            ("1024", "1 MB"),
            ("2048", "2 MB"),
            ("4096", "4 MB"),
            ("8192", "8 MB"),
            ("16384", "16 MB"),
            ("32768", "32 MB"),
            ("65536", "64 MB"),
            ("131072", "128 MB"),
            ("262144", "256 MB"),
        ]
    },

    "audio_buffer_target_bytes": {
        "default": "8192",
        "description": N_("Audio buffer target size (bytes)"),
        "type": "integer",
        "min": 1024,
        "max": 32768,
    },

    "audio_buffer_target_size": {
        "default": "40",
        "description": N_("Audio buffer target size (ms)"),
        "type": "integer",
        "min": 1,
        "max": 100,
    },

    "audio_frequency": {
        "default": "48000",
        "description": N_("Audio output frequency"),
        "type": "choice",
        "values": [
            ("48000", "48000 Hz"),
            ("44100", "44100 Hz"),
            ("22050", "22050 Hz"),
            ("11025", "11025 Hz"),
        ]
    },

    "automatic_input_grab": {
        "default": "1",
        "description": N_("Grab Input on Click"),
        "type": "boolean",
    },

    "blizzard_scsi_kit": {
        "default": "0",
        "description": N_("Blizzard SCSI Kit"),
        "type": "boolean",
    },

    "bsdsocket_library": {
        "default": "0",
        "description": N_("UAE bsdsocket.library"),
        "type": "boolean",
    },

    "builtin_configs": {
        "default": "1",
        "description": N_("Include built-in configurations"),
        "type": "boolean",
    },

    "cdrom_drive_count": {
        "default": "",
        "description": N_("CD-ROM Drive Count"),
        "type": "Choice",
        "values": [
            ("0", "0"),
            ("1", "1"),
        ]
    },

    "chip_memory": {
        "default": "",
        "description": N_("Chip RAM"),
        "type": "Choice",
    },

    "config_feature": {
        "default": "0",
        "description": N_(
            "Enable experimental config visualization (requires restart)"),
        "type": "boolean",
    },

    "cpu": {
        "default": "",
        "description": N_("CPU"),
        "type": "Choice",
        "values": [
            ("68000", "68000"),
            ("68010", "68010"),
            ("68EC020", "68EC020"),
            ("68020", "68020"),
            ("68EC030", "68EC030"),
            ("68030", "68030"),
            ("68EC040", "68EC040"),
            ("68LC040", "68LC040"),
            ("68040-NOMMU", "68040-NOMMU"),
            ("68040", "68040"),
            ("68EC060", "68EC060"),
            ("68LC060", "68LC060"),
            ("68060-NOMMU", "68060-NOMMU"),
            ("68060", "68060"),
        ]
    },

    "cpu_idle": {
        "default": "",
        "description": N_(
            "Relax host CPU usage when using fastest-possible CPU"),
        "type": "integer",
        "min": 0,
        "max": 10,
    },

    "database_arcade": {
        "default": "",
        "description": N_("Enable/disable use of the Arcade game database"),
        "type": "boolean",
    },

    "database_auth": {
        "default": "",
        "description": N_("Game database authentication"),
        "type": "string",
    },

    "database_dos": {
        "default": "",
        "description": N_("Enable/disable use of the DOS game database"),
        "type": "boolean",
    },

    "database_email": {
        "default": "",
        "description": N_("Game database email"),
        "type": "string",
    },

    "database_feature": {
        "default": "0",
        "description": N_("Enable online database support (requires restart)"),
        "type": "boolean",
    },

    "database_gba": {
        "default": "",
        "description": N_(
            "Enable/disable use of the Game Boy Advance database"),
        "type": "boolean",
    },

    "database_locker": {
        "default": "",
        "description": N_("Enable/disable use of OAGD.net locker"),
        "type": "boolean",
    },

    "database_nes": {
        "default": "",
        "description": N_("Enable/disable use of the Nintendo (NES) database"),
        "type": "boolean",
    },

    "database_password": {
        "default": "",
        "description": N_("Game database password"),
        "type": "string",
    },

    "database_server": {
        "default": "oagd.net",
        "description": N_("Game Database Server"),
        "type": "string",
    },

    "database_show_adult": {
        "default": "0",
        "description": N_("Adult-Themed Games"),
        "type": "boolean",
    },

    "database_show_games": {
        "default": "1",
        "description": N_("Database Games"),
        "type": "choice",
        "values": [
            ("0", N_("All Games")),
            ("1", N_("Available and Downloadable Games")),
            ("2", N_("Available and Auto-Downloadable Games")),
            ("3", N_("Available Games")),
        ]
    },

    "database_snes": {
        "default": "",
        "description": N_("Enable/disable use of the Super Nintendo database"),
        "type": "boolean",
    },

    "database_username": {
        "default": "",
        "description": N_("Game database user name"),
        "type": "string",
    },

    "device_id": {
        "default": "",
        "description": N_("Device ID used with OAGD.net authentication"),
        "type": "string",
    },

    "dongle_type": {
        "default": "",
        "description": N_("Dongle"),
        "type": "Choice",
        "values": [
            ("robocop 3", "robocop 3"),
            ("leaderboard", "leaderboard"),
            ("b.a.t. ii", "b.a.t. ii"),
            ("italy'90 soccer", "italy'90 soccer"),
            ("dames grand maitre", "dames grand maitre"),
            ("rugby coach", "rugby coach"),
            ("cricket captain", "cricket captain"),
            ("leviathan", "leviathan"),
        ]
    },

    "fade_in_duration": {
        "default": "0",
        "description": N_("Fade-in Duration on Start"),
        "type": "",
    },

    "floppy_drive_count": {
        "default": "",
        "description": N_("Floppy Drive Count"),
        "type": "Choice",
        "values": [
            ("0", "0"),
            ("1", "1"),
            ("2", "2"),
            ("3", "3"),
            ("4", "4"),
        ]
    },

    "floppy_drive_speed": {
        "default": "100",
        "description": N_("Floppy Drive Speed"),
        "type": "Choice",
        "values": [
            ("0", N_("Turbo")),
            ("100", "100%"),
            ("200", "200 %"),
            ("400", "400 %"),
            ("800", "800 %"),
        ]
    },

    "floppy_drive_volume": {
        "default": "67",
        "description": N_("Floppy Drive Volume"),
        "type": "integer",
        "min": 0,
        "max": 100,
    },

    "floppy_drive_volume_empty": {
        "default": "67",
        "description": N_("Empty Floppy Drive Volume"),
        "type": "integer",
        "min": 0,
        "max": 100,
    },

    "fsaa": {
        "default": "0",
        "description": N_("Full-scene anti-aliasing (FSAA)"),
        "type": "choice",
        "values": [
            ("0", N_("Off")),
            ("2", "2x2"),
            ("4", "4x4"),
            ("8", "8x8"),
        ]
    },

    "fullscreen": {
        "default": "0",
        "description": N_("Start FS-UAE in fullscreen mode"),
        "type": "boolean",
    },

    "graphics_card": {
        "default": "none",
        "description": N_("Graphics Card"),
        "type": "Choice",
        "values": [
            ("none", N_("None")),
            ("uaegfx", "UAEGFX"),
            ("uaegfx-z2", "UAEGFX Zorro II"),
            ("uaegfx-z3", "UAEGFX Zorro III"),
            ("picasso-ii", "Picasso II Zorro II"),
            ("picasso-ii+", "Picasso II+ Zorro II"),
            ("picasso-iv", "Picasso IV"),
            ("picasso-iv-z2", "Picasso IV Zorro II"),
            ("picasso-iv-z3", "Picasso IV Zorro III"),
        ]
    },

    "graphics_memory": {
        "default": "",
        "description": N_("Graphics Card VRAM"),
        "type": "Choice",
        "values": [
            ("1024", "1 MB"),
            ("2048", "2 MB"),
            ("4096", "4 MB"),
            ("8192", "8 MB"),
            ("16384", "16 MB"),
            ("32768", "32 MB"),
            ("65536", "64 MB"),
            ("131072", "128 MB"),
            ("262144", "256 MB"),
        ]
    },

    "initial_input_grab": {
        "default": "",
        "description": N_("Grab Input on FS-UAE Startup"),
        "type": "boolean",
    },

    "irc_nick": {
        "default": "",
        "description": N_("IRC nickname"),
        "type": "string",
    },

    "irc_server": {
        "default": "irc.fengestad.no",
        "description": N_("Custom IRC server address"),
        "type": "string",
    },

    "keep_aspect": {
        "default": "0",
        "description": N_("Keep aspect ratio when scaling (do not stretch)"),
        "type": "boolean",
    },

    "keyboard_input_grab": {
        "default": "1",
        "description": N_("Grab keyboard when input is grabbed"),
        "type": "boolean",
    },

    "keyboard_key_backslash": {
        "default": "action_key_backslash",
        "description": N_("Host Key BACKSLASH"),
        "type": "Choice",
        "values": [
            ("action_key_2b", "Amiga Key 0x2B"),
            ("action_key_30", "Amiga Key 0x30"),
            ("action_key_backslash", "Amiga Key Backslash"),
            ("action_key_equals", "Amiga Key Equals"),
        ]
    },

    "keyboard_key_equals": {
        "default": "action_key_equals",
        "description": N_("Host Key EQUALS"),
        "type": "Choice",
        "values": [
            ("action_key_2b", "Amiga Key 0x2B"),
            ("action_key_30", "Amiga Key 0x30"),
            ("action_key_backslash", "Amiga Key Backslash"),
            ("action_key_equals", "Amiga Key Equals"),
        ]
    },

    "keyboard_key_insert": {
        "default": "action_key_2b",
        "description": N_("Host Key INSERT"),
        "type": "Choice",
        "values": [
            ("action_key_2b", "Amiga Key 0x2B"),
            ("action_key_30", "Amiga Key 0x30"),
            ("action_key_backslash", "Amiga Key Backslash"),
            ("action_key_equals", "Amiga Key Equals"),
        ]
    },

    "keyboard_key_less": {
        "default": "action_key_30",
        "description": N_("Host Key LESS"),
        "type": "Choice",
        "values": [
            ("action_key_2b", "Amiga Key 0x2B"),
            ("action_key_30", "Amiga Key 0x30"),
            ("action_key_backslash", "Amiga Key Backslash"),
            ("action_key_equals", "Amiga Key Equals"),
        ]
    },

    "kickstart_setup": {
        "default": "1",
        "description": N_(
            "Show kickstart setup page on startup when all ROMs are missing"),
        "type": "boolean",
    },

    "launcher_theme": {
        "default": "fusion",
        "description": N_("FS-UAE Launcher Theme"),
        "type": "Choice",
        "values": [
            ("native", N_("Native")),
            ("fusion", "Fusion Auto"),
            ("fusion-plain", "Fusion Plain"),
            ("fusion-adwaita", "Fusion Adwaita"),
            ("fusion-dark", "Fusion Dark"),
        ]
    },

    "load_state": {
        "default": "",
        "description": N_("Load state by number"),
        "type": "integer",
        "min": 1,
        "max": 9,
    },

    "log_autoscale": {
        "default": "0",
        "description": N_("Log Autoscale Changes"),
        "type": "boolean",
    },

    "log_input": {
        "default": "0",
        "description": N_("Log Input Events"),
        "type": "boolean",
    },

    "log_query_plans": {
        "default": "",
        "description": N_("Log database query plans"),
        "type": "",
    },

    "low_latency_vsync": {
        "default": "0",
        "description": N_("Low latency video sync"),
        "type": "boolean",
    },

    "middle_click_ungrab": {
        "default": "1",
        "description": N_("Ungrab Input on Middle Mouse Button"),
        "type": "boolean",
    },

    "min_first_line_ntsc": {
        "default": "21",
        "description": N_("First rendered line (NTSC)"),
        "type": "",
    },

    "min_first_line_pal": {
        "default": "26",
        "description": N_("First rendered line (PAL)"),
        "type": "",
    },

    "monitor": {
        "default": "middle-left",
        "description": N_("Monitor to display FS-UAE on (fullscreen)"),
        "type": "choice",
        "values": [
            ("left", N_("Left")),
            ("middle-left", N_("Middle Left")),
            ("middle-right", N_("Middle Right")),
            ("right", N_("Right")),
        ]
    },

    "mouse_speed": {
        "default": "100",
        "description": N_("Mouse Speed (%)"),
        "type": "integer",
        "min": 1,
        "max": 500,
    },

    "netplay_feature": {
        "default": "0",
        "description": N_(
            "Enable experimental net play GUI (requires restart)"),
        "type": "boolean",
    },

    "netplay_tag": {
        "default": "UNK",
        "description": N_("Net play tag (max 3 characters)"),
        "type": "string",
    },

    "rtg_scanlines": {
        "default": "0",
        "description": N_("Render scan lines in RTG graphics mode"),
        "type": "boolean",
    },

    "scanlines": {
        "default": "0",
        "description": N_("Render scan lines"),
        "type": "boolean",
    },

    "sound_card": {
        "default": "0",
        "description": N_("Sound Card"),
        "type": "Choice",
        "values": [
            ("0", N_("None")),
            ("toccata", "Toccata"),
        ]
    },

    "stereo_separation": {
        "default": "70",
        "description": N_("Stereo Separation"),
        "type": "choice",
        "values": [
            ("100", "100%"),
            ("90", "90%"),
            ("80", "80%"),
            ("70", "70%"),
            ("60", "60%"),
            ("50", "50%"),
            ("40", "40%"),
            ("30", "30%"),
            ("20", "20%"),
            ("10", "10%"),
            ("0", "0%"),
        ]
    },

    "swap_ctrl_keys": {
        "default": "0",
        "description": N_("Swap left and right CTRL keys"),
        "type": "boolean",
    },

    "texture_filter": {
        "default": "linear",
        "description": N_("Texture filter"),
        "type": "choice",
        "values": [
            ("nearest", "GL_NEAREST"),
            ("linear", "GL_LINEAR"),
        ]
    },

    "texture_format": {
        "default": "",
        "description": N_("Video texture format (on the GPU)"),
        "type": "choice",
        "values": [
            ("rgb", "GL_RGB"),
            ("rgb8", "GL_RGB8"),
            ("rgba", "GL_RGBA"),
            ("rgba8", "GL_RGBA8"),
            ("rgb5", "GL_RGB5"),
            ("rgb5_1", "GL_RGB5_1"),
        ]
    },

    "uae_a2065": {
        "default": "",
        "description": N_("uae_a2065"),
        "type": "",
        "values": [
            ("slirp", "slirp"),
        ]
    },

    "uae_a3000mem_size": {
        "default": "",
        "description": N_("Size in megabytes of motherboard fast memory"),
        "type": "integer",
        "min": 0,
        "max": 65536,
    },

    "uae_chipset_compatible": {
        "default": "",
        "description": N_(
            "Enable default chipset features for a specific model"),
        "type": "choice",
        "values": [
            ("-", "-"),
            ("Generic", "Generic"),
            ("CDTV", "CDTV"),
            ("CD32", "CD32"),
            ("A500", "A500"),
            ("A500+", "A500+"),
            ("A600", "A600"),
            ("A1000", "A1000"),
            ("A1200", "A1200"),
            ("A2000", "A2000"),
            ("A3000", "A3000"),
            ("A3000T", "A3000T"),
            ("A4000", "A4000"),
            ("A4000T", "A4000T"),
        ]
    },

    "uae_cpu_frequency": {
        "default": "",
        "description": N_(
            "Specify the frequency of the emulated CPU in cycle-exact modes"),
        "type": "float",
        "min": 1.0,
        "max": 100.0,
    },

    "uae_cpu_multiplier": {
        "default": "",
        "description": N_("FIXME"),
        "type": "integer",
        "min": 0,
        "max": 256,
    },

    "uae_cpu_speed": {
        "default": "",
        "description": N_("Enable/disable fastest possible CPU speed"),
        "type": "choice",
        "values": [
            ("real", N_("Approximate A500/A1200 or cycle-exact")),
            ("max", N_("Fastest possible")),
        ]
    },

    "uae_cpu_throttle": {
        "default": "",
        "description": N_("FIXME"),
        "type": "float",
        "min": -900.0,
        "max": 5000.0,
    },

    "uae_fastmem2_size": {
        "default": "0",
        "description": N_(
            "Size in MB of Zorro-II Fast RAM (second) expansion board"),
        "type": "choice",
        "values": [
            ("0", "0"),
            ("1", "1"),
            ("2", "2"),
            ("4", "4"),
        ]
    },

    "uae_fastmem_autoconfig": {
        "default": "1",
        "description": N_("Autoconfig Z2 Fast RAM"),
        "type": "boolean",
    },

    "uae_fastmem_size": {
        "default": "0",
        "description": N_("Size in MB of Zorro-II Fast RAM expansion board"),
        "type": "choice",
        "values": [
            ("0", "0"),
            ("1", "1"),
            ("2", "2"),
            ("4", "4"),
            ("8", "8"),
        ]
    },

    "uae_force_0x10000000_z3": {
        "default": "false",
        "description": N_("Force Zorro-III address space at 0x10000000"),
        "type": "boolean",
    },

    "uae_gfx_linemode": {
        "default": "",
        "description": N_(
            "Controls how lines are doubled and interlaced modes are handled"),
        "type": "choice",
        "values": [
            ("none", "Single / Single"),
            ("double", "Double / Double Frames"),
            ("double2", "Double / Double Fields"),
            ("double3", "Double / Double Fields+"),
            ("scanlines", "Scanlines / Double Frames"),
            ("scanlines2", "Scanlines / Double Fields"),
            ("scanlines3", "Scanlines / Double Fields+"),
            ("scanlines2p", "Double Fields / Double Frames"),
            ("scanlines2p2", "Double Fields / Double Fields"),
            ("scanlines2p3", "Double Fields / Double Fields+"),
            ("scanlines3p", "Double Fields+ / Double Frames"),
            ("scanlines3p2", "Double Fields+ / Double Fields"),
            ("scanlines3p3", "Double Fields+ / Double Fields+"),
        ]
    },

    "uae_mbresmem_size": {
        "default": "",
        "description": N_("Size in megabytes of processor slot fast memory"),
        "type": "integer",
        "min": 0,
        "max": 131072,
    },

    "uae_rtc": {
        "default": "auto",
        "description": N_("Enable a real time clock (RTC) module."),
        "type": "Choice",
        "values": [
            ("auto", N_("Auto")),
            ("none", N_("None")),
            ("MSM6242B", "Oki MSM6242B)- RTC module in A500/500+/600/1200/2000 models"),
            ("RP5C01A", "Ricoh RP5C01A"),
            ("MSM6242B_A2000", "A2000 MSM6242B"),
        ]
    },

    "uae_sana2": {
        "default": "false",
        "description": N_("uae_sana2"),
        "type": "BooleanUAE,",
    },

    "uae_slirp_implementation": {
        "default": "auto",
        "description": N_("Slirp Implementation"),
        "type": "Choice",
        "values": [
            ("auto", "auto"),
            ("none", "none"),
            ("builtin", "builtin"),
            ("qemu", "qemu"),
        ]
    },

    "uae_sound_output": {
        "default": "",
        "description": N_("Sound emulation"),
        "type": "",
        "values": [
            ("none", "Disabled"),
            ("interrupts", "Emulated, No Output"),
            ("exact", "Enabled"),
        ]
    },

    "uae_toccata": {
        "default": "",
        "description": N_("Toccata Z2 sound card emulation"),
        "type": "uaeyesno",
    },

    "uae_z3chipmem_size": {
        "default": "",
        "description": "",
        "type": "integer",
    },

    "uae_z3mapping": {
        "default": "auto",
        "description": N_("JIT Direct compatible Z3 memory mapping"),
        "type": "choice",
    },

    "uae_z3mem2_size": {
        "default": "",
        "description": "",
        "type": "integer",
    },

    "uae_z3mem_size": {
        "default": "",
        "description": N_("Size in MB of Zorro-III Fast RAM expansion board"),
        "type": "integer",
    },

    "uaegfx_card": {
        "default": "0",
        "description": N_("uaegfx_card"),
        "type": "boolean",
    },

    "uaem_write_flags": {
        "default": "1",
        "description": N_("Write .uaem metadata files"),
        "type": "flags",
    },

    "video_format": {
        "default": "bgra",
        "description": N_("Video buffer format and color depth"),
        "type": "choice",
        "values": [
            ("bgra", N_("32-bit BGRA")),
            ("rgba", N_("32-bit RGBA")),
            ("rgb565", N_("16-bit")),
        ]
    },

    "video_sync": {
        "default": "off",
        "description": N_("Video synchronization"),
        "type": "choice",
        "values": [
            ("auto", N_("Auto")),
            ("vblank", N_("Buffer swap only")),
            ("off", N_("Off")),
        ]
    },

    "video_sync_method": {
        "default": "",
        "description": N_("Video synchronization method"),
        "type": "choice",
        "values": [
            ("swap", "Swap"),
            ("swap-finish", "Swap-Finish"),
            ("finish-swap-finish", "Finish-Swap-Finish"),
            ("finish-sleep-swap-finish", "Finish-Sleep-Swap-Finish"),
            ("sleep-swap-finish", "Sleep-Swap-Finish"),
            ("swap-fence", "Swap-Fence"),
            ("swap-sleep-fence", "Swap-Sleep-Fence"),
        ]
    },

    "volume": {
        "default": "100",
        "description": N_("Main Volume"),
        "type": "integer",
        "min": 0,
        "max": 100,
    },

    "whdload_splash_delay": {
        "default": "200",
        "description": N_("WHDLoad splash delay"),
        "type": "integer",
        "min": -1,
        "max": 500,
    },

    "window_border": {
        "default": "",
        "description": N_("Show window border and decorations"),
        "type": "boolean",
    },

    "zoom": {
        "default": "auto",
        "description": N_("Zoom Amiga display (crop)"),
        "type": "choice",
        "values": [
            ("auto", N_("Auto")),
            ("auto+border", N_("Auto + Border")),
            ("full", N_("Full Frame")),
            ("640x400", "640x400"),
            ("640x400+border", N_("640x400 + Border")),
            ("640x480", "640x480"),
            ("640x480+border", N_("640x480 + Border")),
            ("640x512", "640x512"),
            ("640x512+border", N_("640x512 + Border")),
            ("704x540", "704x540"),
            ("704x566", "704x566"),
            ("724x566", "724x566"),
        ]
    },

}
