# Automatically generated - do not edit by hand


class Option(object):
    """Constants for option names."""    
    AUDIO_BUFFER_TARGET_BYTES = "audio_buffer_target_bytes"
    AUDIO_BUFFER_TARGET_SIZE = "audio_buffer_target_size"
    AUDIO_FREQUENCY = "audio_frequency"
    AUTOMATIC_INPUT_GRAB = "automatic_input_grab"
    BUILTIN_CONFIGS = "builtin_configs"
    CONFIG_FEATURE = "config_feature"
    CPU_IDLE = "cpu_idle"
    DATABASE_AUTH = "database_auth"
    DATABASE_EMAIL = "database_email"
    DATABASE_FEATURE = "database_feature"
    DATABASE_LOCKER = "database_locker"
    DATABASE_PASSWORD = "database_password"
    DATABASE_SERVER = "database_server"
    DATABASE_SHOW_ADULT = "database_show_adult"
    DATABASE_SHOW_GAMES = "database_show_games"
    DATABASE_USERNAME = "database_username"
    DEVICE_ID = "device_id"
    FLOPPY_DRIVE_VOLUME = "floppy_drive_volume"
    FSAA = "fsaa"
    FULLSCREEN = "fullscreen"
    GRAPHICS_CARD = "graphics_card"
    GRAPHICS_MEMORY = "graphics_memory"
    INITIAL_INPUT_GRAB = "initial_input_grab"
    IRC_NICK = "irc_nick"
    IRC_SERVER = "irc_server"
    KEEP_ASPECT = "keep_aspect"
    KEYBOARD_INPUT_GRAB = "keyboard_input_grab"
    KICKSTART_SETUP = "kickstart_setup"
    LOAD_STATE = "load_state"
    LOG_QUERY_PLANS = "log_query_plans"
    LOW_LATENCY_VSYNC = "low_latency_vsync"
    MIDDLE_CLICK_UNGRAB = "middle_click_ungrab"
    MIN_FIRST_LINE_NTSC = "min_first_line_ntsc"
    MIN_FIRST_LINE_PAL = "min_first_line_pal"
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
    UAE_SOUND_OUTPUT = "uae_sound_output"
    UAE_Z3CHIPMEM_SIZE = "uae_z3chipmem_size"
    UAE_Z3MAPPING = "uae_z3mapping"
    UAE_Z3MEM2_SIZE = "uae_z3mem2_size"
    UAE_Z3MEM_SIZE = "uae_z3mem_size"
    UAEM_WRITE_FLAGS = "uaem_write_flags"
    VIDEO_FORMAT = "video_format"
    VIDEO_SYNC = "video_sync"
    VIDEO_SYNC_METHOD = "video_sync_method"
    VOLUME = "volume"
    ZOOM = "zoom"


class Options(object):

    @staticmethod
    def get(name):
        return options[name]


N_ = lambda x: x


options = {

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
        "description": N_(
            "Grab mouse and keyboard input when clicking on FS-UAE window"),
        "type": "boolean",
    },

    "builtin_configs": {
        "default": "1",
        "description": N_("Include built-in configurations"),
        "type": "boolean",
    },

    "config_feature": {
        "default": "0",
        "description": N_("Enable new config feature (requires restart)"),
        "type": "boolean",
    },

    "cpu_idle": {
        "default": "",
        "description": N_(
            "Relax host CPU usage when using fastest-possible CPU"),
        "type": "integer",
        "min": 0,
        "max": 10,
    },

    "database_auth": {
        "default": "",
        "description": N_("Game database authentication"),
        "type": "string",
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

    "database_locker": {
        "default": "",
        "description": N_("Enable/disable use of OAGD.net locker"),
        "type": "boolean",
    },

    "database_password": {
        "default": "",
        "description": N_("Game database password"),
        "type": "string",
    },

    "database_server": {
        "default": "oagd.net",
        "description": N_("Custom game database server address"),
        "type": "string",
    },

    "database_show_adult": {
        "default": "0",
        "description": N_("Include adult-themed games"),
        "type": "boolean",
    },

    "database_show_games": {
        "default": "1",
        "description": N_("Show games from database"),
        "type": "choice",
        "values": [
            ("0", N_("All games in the database")),
            ("1", N_("Games you have and all downloadable games")),
            ("2", N_("Games you have and automatically downloadable")),
            ("3", N_("Only games you have")),
        ]
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

    "floppy_drive_volume": {
        "default": "20",
        "description": N_("Floppy drive volume"),
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
        "description": N_(""),
        "type": "choice",
        "values": [
            ("none", N_("None")),
            ("uaegfx", N_("UAEGFX (Auto)")),
            ("uaegfx-z2", N_("UAEGFX (Zorro II)")),
            ("uaegfx-z3", N_("UAEGFX (Zorro III)")),
            ("picasso-ii", N_("Picasso II (Zorro II)")),
            ("picasso-ii+", N_("Picasso II+ (Zorro II)")),
            ("picasso-iv", N_("Picasso IV (Auto)")),
            ("picasso-iv-z2", N_("Picasso IV (Zorro II)")),
            ("picasso-iv-z3", N_("Picasso IV (Zorro III)")),
        ]
    },

    "graphics_memory": {
        "default": "",
        "description": N_(
            "Override the amount of graphics memory on the graphics card"),
        "type": "integer",
    },

    "initial_input_grab": {
        "default": "",
        "description": N_("Grab mouse and keyboard input when FS-UAE starts"),
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

    "kickstart_setup": {
        "default": "1",
        "description": N_(
            "Show kickstart setup page on startup when all ROMs are missing"),
        "type": "boolean",
    },

    "load_state": {
        "default": "",
        "description": N_("Load state by number"),
        "type": "integer",
        "min": 1,
        "max": 9,
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
        "description": N_("Ungrab mouse and keyboard on middle mouse click"),
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

    "mouse_speed": {
        "default": "100",
        "description": N_("Mouse speed (%)"),
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
        "description": N_(""),
        "type": "choice",
        "values": [
            ("0", N_("None")),
            ("toccata", N_("Toccata Z2")),
        ]
    },

    "stereo_separation": {
        "default": "100",
        "description": N_("Stereo separation"),
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
            ("none", N_("Single / Single")),
            ("double", N_("Double / Double Frames")),
            ("double2", N_("Double / Double Fields")),
            ("double3", N_("Double / Double Fields+")),
            ("scanlines", N_("Scanlines / Double Frames")),
            ("scanlines2", N_("Scanlines / Double Fields")),
            ("scanlines3", N_("Scanlines / Double Fields+")),
            ("scanlines2p", N_("Double Fields / Double Frames")),
            ("scanlines2p2", N_("Double Fields / Double Fields")),
            ("scanlines2p3", N_("Double Fields / Double Fields+")),
            ("scanlines3p", N_("Double Fields+ / Double Frames")),
            ("scanlines3p2", N_("Double Fields+ / Double Fields")),
            ("scanlines3p3", N_("Double Fields+ / Double Fields+")),
        ]
    },

    "uae_mbresmem_size": {
        "default": "",
        "description": N_("Size in megabytes of processor slot fast memory"),
        "type": "integer",
        "min": 0,
        "max": 131072,
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

    "uae_z3chipmem_size": {
        "default": "",
        "description": N_(""),
        "type": "integer",
    },

    "uae_z3mapping": {
        "default": "auto",
        "description": N_("JIT Direct compatible Z3 memory mapping"),
        "type": "choice",
    },

    "uae_z3mem2_size": {
        "default": "",
        "description": N_(""),
        "type": "integer",
    },

    "uae_z3mem_size": {
        "default": "",
        "description": N_("Size in MB of Zorro-III Fast RAM expansion board"),
        "type": "integer",
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
        "description": N_("Main volume control"),
        "type": "integer",
        "min": 0,
        "max": 100,
    },

    "zoom": {
        "default": "auto",
        "description": N_("Zoom Amiga display (crop)"),
        "type": "choice",
        "values": [
            ("auto", N_("Auto")),
            ("full", N_("Full Frame")),
            ("640x400", "640x400"),
            ("640x480", "640x480"),
            ("640x512", "640x512"),
            ("auto+border", N_("Auto + Border")),
            ("640x400+border", N_("640x400 + Border")),
            ("640x480+border", N_("640x480 + Border")),
            ("640x512+border", N_("640x512 + Border")),
        ]
    },

}
