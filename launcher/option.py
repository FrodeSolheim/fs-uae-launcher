# Automatically generated - do not edit by hand

from fsgs.option import Option as BaseOption


# noinspection PyClassHasNoInit
class Option(BaseOption):
    @staticmethod
    def get(name):
        return options[name]


# noinspection PyPep8Naming
def N_(x):
    return x


options = {
    Option.A2600_DATABASE: {
        "default": "0",
        "description": ("Enable/disable use of the Atari 2600 database"),
        "type": "Boolean",
    },
    Option.A5200_DATABASE: {
        "default": "0",
        "description": ("Enable/disable use of the Atari 5200 database"),
        "type": "Boolean",
    },
    Option.A7800_DATABASE: {
        "default": "0",
        "description": ("Enable/disable use of the Atari 7800 database"),
        "type": "Boolean",
    },
    Option.A7800_MODEL: {
        "default": "ntsc",
        "description": ("Atari 7800 Model"),
        "type": "Choice",
        "values": [
            ("ntsc", "NTSC"),
            ("pal", "PAL"),
        ]
    },
    Option.A7800_PORT_1_TYPE: {
        "default": "joystick",
        "description": ("Atari 7800 Port 1"),
        "type": "Choice",
        "values": [
            ("none", N_("None")),
            ("joystick", N_("Joystick")),
        ]
    },
    Option.A7800_PORT_2_TYPE: {
        "default": "joystick",
        "description": ("Atari 7800 Port 2"),
        "type": "Choice",
        "values": [
            ("none", N_("None")),
            ("joystick", N_("Joystick")),
        ]
    },
    Option.ACCELERATOR: {
        "default": "0",
        "description": N_("Accelerator Board"),
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
    Option.ACCELERATOR_MEMORY: {
        "default": "",
        "description": N_("Accelerator RAM"),
        "type": "Choice",
        "values": [
            ("0", "0 MB"),
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
    Option.AMIGA_DATABASE: {
        "default": "1",
        "description": ("Enable/disable use of the Amiga game database"),
        "type": "Boolean",
    },
    Option.AMIGA_DRIVER: {
        "default": "fs-uae",
        "description": ("Amiga Game Driver"),
        "type": "Choice",
        "values": [
            ("fs-uae", "FS-UAE"),
        ]
    },
    Option.ARCADE_DATABASE: {
        "default": "0",
        "description": ("Enable/disable use of the Arcade game database"),
        "type": "Boolean",
    },
    Option.ARCADE_FULLSCREEN: {
        "default": "1",
        "description": N_("Arcade Fullscreen"),
        "type": "boolean",
    },
    Option.ARCADE_INITIAL_FAVORITES: {
        "default": "0",
        "description": N_("Arcade starts with favorites filter"),
        "type": "Boolean",
    },
    Option.ARCADE_SEARCH: {
        "default": "",
        "description": ("Enable/disable search function in Arcade"),
        "type": "boolean",
    },
    Option.ARCADE_SHUTDOWN: {
        "default": "",
        "description": ("Arcade Shutdown Command"),
        "type": "",
    },
    Option.ARCADE_THEME: {
        "default": "blue",
        "description": N_("Arcade theme"),
        "type": "Choice",
        "values": [
            ("blue", N_("Blue")),
            ("red", N_("Red")),
        ]
    },
    Option.ATARI_DATABASE: {
        "default": "0",
        "description": ("Enable/disable use of the Atari ST game database"),
        "type": "Boolean",
    },
    Option.ATARI_MODEL: {
        "default": "1040st",
        "description": ("Atari ST Model"),
        "type": "Choice",
        "values": [
            ("520st", "520ST"),
            ("1040st", "1040ST"),
            ("520ste", "520STE"),
            ("1040ste", "1040STE"),
        ]
    },
    Option.AUDIO_BUFFER_TARGET_BYTES: {
        "default": "8192",
        "description": ("Audio buffer target size (bytes)"),
        "type": "integer",
        "min": 1024,
        "max": 32768,
    },
    Option.AUDIO_BUFFER_TARGET_SIZE: {
        "default": "40",
        "description": N_("Audio buffer target size (ms)"),
        "type": "integer",
        "min": 1,
        "max": 100,
    },
    Option.AUDIO_FREQUENCY: {
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
    Option.AUTO_LOAD: {
        "default": "1",
        "description": ("Auto-Load Games"),
        "type": "Boolean",
    },
    Option.AUTO_QUIT: {
        "default": "1",
        "description": ("Auto-Quit"),
        "type": "Boolean",
    },
    Option.AUTOMATIC_INPUT_GRAB: {
        "default": "1",
        "description": N_("Grab Input on Click"),
        "type": "boolean",
    },
    Option.BEZEL: {
        "default": "1",
        "description": ("Bezel"),
        "type": "Choice",
        "values": [
            ("1", N_("Show Bezel")),
            ("0", N_("Hide Bezel")),
        ]
    },
    Option.BLIZZARD_SCSI_KIT: {
        "default": "0",
        "description": N_("Blizzard SCSI Kit"),
        "type": "boolean",
    },
    Option.BORDER: {
        "default": "1",
        "description": ("Border"),
        "type": "Choice",
        "values": [
            ("1", N_("Small Border")),
            ("0", N_("No Border")),
            ("large", N_("Large Border")),
        ]
    },
    Option.BSDSOCKET_LIBRARY: {
        "default": "0",
        "description": ("UAE bsdsocket.library"),
        "type": "boolean",
    },
    Option.BUILTIN_CONFIGS: {
        "default": "1",
        "description": ("Include built-in configurations"),
        "type": "boolean",
    },
    Option.C64_DATABASE: {
        "default": "0",
        "description": (
            "Enable/disable use of the Commodore 64 (C64) database"),
        "type": "Boolean",
    },
    Option.C64_MODEL: {
        "default": "c64c",
        "description": ("Commodore 64 Model"),
        "type": "Choice",
        "values": [
            ("c64c", "C64C"),
            ("c64c/1541-ii", "C64C, 1541-II Floppy Drive"),
            ("c64", "C64"),
        ]
    },
    Option.C64_PALETTE: {
        "default": "vice",
        "description": ("C64 Palette"),
        "type": "Choice",
        "values": [
            ("c64hq", "C64HQ"),
            ("c64s", "C64S"),
            ("ccs64", "CCS64"),
            ("community-colors", "Community"),
            ("deekay", "Deekay"),
            ("frodo", "Frodo"),
            ("godot", "Godot"),
            ("pc64", "PC64"),
            ("pepto-ntsc-sony", "Pepto NTSC Sony"),
            ("pepto-ntsc", "Pepto NTSC"),
            ("pepto-palold", "Pepto PAL-Old"),
            ("pepto-pal", "Pepto PAL"),
            ("ptoing", "Ptoing"),
            ("rgb", "RGB"),
            ("vice", "Vice"),
        ]
    },
    Option.C64_PORT_1_TYPE: {
        "default": "joystick",
        "description": ("C64 Port 1"),
        "type": "Choice",
        "values": [
            ("none", N_("None")),
            ("joystick", N_("Joystick")),
        ]
    },
    Option.C64_PORT_2_TYPE: {
        "default": "joystick",
        "description": ("C64 Port 2"),
        "type": "Choice",
        "values": [
            ("none", N_("None")),
            ("joystick", N_("Joystick")),
        ]
    },
    Option.CD32_DATABASE: {
        "default": "1",
        "description": ("Enable/disable use of the CD32 game database"),
        "type": "Boolean",
    },
    Option.CDROM_DRIVE_0_DELAY: {
        "default": "0",
        "description": N_("Delayed CD-ROM Insert"),
        "type": "Boolean",
    },
    Option.CDROM_DRIVE_COUNT: {
        "default": "",
        "description": ("CD-ROM Drive Count"),
        "type": "Choice",
        "values": [
            ("0", "0"),
            ("1", "1"),
        ]
    },
    Option.CDTV_DATABASE: {
        "default": "1",
        "description": ("Enable/disable use of the CDTV game database"),
        "type": "Boolean",
    },
    Option.CHEATS: {
        "default": "0",
        "description": ("Cheats"),
        "type": "Boolean",
    },
    Option.CHIP_MEMORY: {
        "default": "",
        "description": N_("Chip RAM"),
        "type": "Choice",
        "values": [
            ("256", "256 KB"),
            ("512", "512 KB"),
            ("1024", "1 MB"),
            ("1536", "1.5 MB"),
            ("2048", "2 MB"),
            ("4096", "4 MB"),
            ("8192", "8 MB"),
        ]
    },
    Option.CPC_DATABASE: {
        "default": "0",
        "description": (
            "Enable/disable use of the Amstrad CPC game database"),
        "type": "Boolean",
    },
    Option.CPU: {
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
    Option.CPU_IDLE: {
        "default": "",
        "description": (
            "Relax host CPU usage when using fastest-possible CPU"),
        "type": "integer",
        "min": 0,
        "max": 10,
    },
    Option.CROP: {
        "default": "1",
        "description": ("Crop"),
        "type": "Choice",
        "values": [
            ("0", N_("Full Frame")),
            ("1", N_("Crop")),
            ("border", N_("Small Border")),
        ]
    },
    Option.DATABASE_AUTH: {
        "default": "",
        "description": ("Game database authentication"),
        "type": "string",
    },
    Option.DATABASE_EMAIL: {
        "default": "",
        "description": ("Game database email"),
        "type": "string",
    },
    Option.DATABASE_FEATURE: {
        "default": "0",
        "description": ("Enable online database support (requires restart)"),
        "type": "boolean",
    },
    Option.DATABASE_LOCKER: {
        "default": "1",
        "description": ("OpenRetro.org Locker"),
        "type": "Boolean",
    },
    Option.DATABASE_PASSWORD: {
        "default": "",
        "description": ("Game database password"),
        "type": "string",
    },
    Option.DATABASE_SERVER: {
        "default": "oagd.net",
        "description": ("Game Database Server"),
        "type": "string",
    },
    Option.DATABASE_SHOW_ADULT: {
        "default": "0",
        "description": N_("Adult-Themed Games"),
        "type": "boolean",
    },
    Option.DATABASE_SHOW_GAMES: {
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
    Option.DATABASE_SHOW_UNPUBLISHED: {
        "default": "0",
        "description": N_("Unpublished Games"),
        "type": "boolean",
    },
    Option.DATABASE_USERNAME: {
        "default": "",
        "description": ("Game database user name"),
        "type": "string",
    },
    Option.DEVELOPER_MODE: {
        "default": "",
        "description": ("Developer Mode"),
        "type": "",
    },
    Option.DEVICE_ID: {
        "default": "",
        "description": ("Device ID used with OAGD.net authentication"),
        "type": "string",
    },
    Option.DONGLE_TYPE: {
        "default": "0",
        "description": N_("Hardware Dongle"),
        "type": "Choice",
        "values": [
            ("0", N_("None")),
            ("robocop 3", "RoboCop 3"),
            ("leaderboard", "Leader Board"),
            ("b.a.t. ii", "B.A.T. II"),
            ("italy'90 soccer", "Italy Soccer '90"),
            ("dames grand maitre", "Dames Grand-Maître"),
            ("rugby coach", "Rugby Coach"),
            ("cricket captain", "Cricket Captain"),
            ("leviathan", "Leviathan"),
        ]
    },
    Option.DOS_DATABASE: {
        "default": "0",
        "description": ("Enable/disable use of the DOS game database"),
        "type": "Boolean",
    },
    Option.DOS_EMULATOR: {
        "default": "dosbox-fs",
        "description": ("DOS Emulator"),
        "type": "Choice",
        "values": [
            ("dosbox-fs", "DOSBox-FS"),
            ("dosbox", "DOSBox"),
            ("dosbox-svn", "DOSBox-SVN"),
        ]
    },
    Option.DOSBOX_SBLASTER_IRQ: {
        "default": "7",
        "description": ("Sound Blaster IRQ"),
        "type": "Choice",
    },
    Option.EFFECT: {
        "default": "2x",
        "description": ("Effect"),
        "type": "Choice",
        "values": [
            ("0", N_("No Effect")),
            ("2x", N_("Pixel Doubling")),
            ("hq2x", "HQ2X"),
            ("scale2x", "Scale2X"),
            ("crt", N_("CRT Emulation")),
        ]
    },
    Option.EMULATOR_PID_FILE: {
        "default": "",
        "description": ("Write emulator PID file"),
        "type": "",
    },
    Option.EXPECT_VERSION: {
        "default": "",
        "description": ("Expect Specific FS-UAE Version"),
        "type": "",
    },
    Option.FADE_IN_DURATION: {
        "default": "500",
        "description": ("Fade-in Duration on Start"),
        "type": "",
    },
    Option.FAST_MEMORY: {
        "default": "",
        "description": N_("Fast RAM"),
        "type": "Choice",
        "values": [
            ("0", "0 MB"),
            ("64", "64 KB"),
            ("128", "128 KB"),
            ("256", "256 KB"),
            ("512", "512 KB"),
            ("1024", "1 MB"),
            ("2048", "2 MB"),
            ("4096", "4 MB"),
            ("8192", "8 MB"),
            ("", ""),
        ]
    },
    Option.FLOPPY_DRIVE_COUNT: {
        "default": "",
        "description": ("Floppy Drive Count"),
        "type": "Choice",
        "values": [
            ("0", "0"),
            ("1", "1"),
            ("2", "2"),
            ("3", "3"),
            ("4", "4"),
        ]
    },
    Option.FLOPPY_DRIVE_SPEED: {
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
    Option.FLOPPY_DRIVE_VOLUME: {
        "default": "20",
        "description": N_("Floppy Drive Volume"),
        "type": "integer",
        "min": 0,
        "max": 100,
    },
    Option.FLOPPY_DRIVE_VOLUME_EMPTY: {
        "default": "25",
        "description": N_("Empty Floppy Drive Volume"),
        "type": "integer",
        "min": 0,
        "max": 100,
    },
    Option.FORCE_ASPECT: {
        "default": "",
        "description": ("Force Aspect"),
        "type": "Double",
    },
    Option.FRAME_TIME: {
        "default": "0",
        "description": ("Frame time (ms)"),
        "type": "",
    },
    Option.FREEZER_CARTRIDGE: {
        "default": "0",
        "description": N_("Freezer Cartridge"),
        "type": "Choice",
        "values": [
            ("0", N_("None")),
            ("hrtmon", N_("HRTMon v2.36 (Built-in)")),
            ("action-replay-2", "Action Replay Mk II v2.14"),
            ("action-replay-3", "Action Replay Mk III v3.17"),
        ]
    },
    Option.FSAA: {
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
    Option.FULL_KEYBOARD: {
        "default": "0",
        "description": N_("Start with full keyboard emulation"),
        "type": "boolean",
    },
    Option.FULLSCREEN: {
        "default": "0",
        "description": N_("Start FS-UAE in fullscreen mode"),
        "type": "boolean",
    },
    Option.FULLSCREEN_MODE: {
        "default": "desktop",
        "description": N_("Fullscreen Mode"),
        "type": "Choice",
        "values": [
            ("fullscreen", N_("Fullscreen")),
            ("desktop", N_("Fullscreen Desktop")),
            ("window", N_("Fullscreen Window")),
        ]
    },
    Option.G_SYNC: {
        "default": "ignore",
        "description": ("G-Sync"),
        "type": "Choice",
        "values": [
            ("ignore", "Ignore"),
            ("1", "On"),
            ("0", "Off (Linux)"),
        ]
    },
    Option.GB_DATABASE: {
        "default": "0",
        "description": ("Enable/disable use of the Game Boy database"),
        "type": "Boolean",
    },
    Option.GB_PORT_1_TYPE: {
        "default": "builtin",
        "description": ("Game Boy Port 1"),
        "type": "Choice",
        "values": [
            ("builtin", N_("Built-in")),
        ]
    },
    Option.GBA_DATABASE: {
        "default": "0",
        "description": (
            "Enable/disable use of the Game Boy Advance database"),
        "type": "Boolean",
    },
    Option.GBA_GAMMA: {
        "default": "1.3",
        "description": ("Game Boy Advance Gamma Adjustment"),
        "type": "Choice",
        "values": [
            ("1.0", "1.0"),
            ("1.1", "1.1"),
            ("1.2", "1.2"),
            ("1.3", "1.3"),
            ("1.4", "1.4"),
            ("1.5", "1.5"),
            ("1.6", "1.6"),
            ("1.7", "1.7"),
            ("1.8", "1.8"),
            ("1.9", "1.9"),
            ("2.0", "2.0"),
            ("2.1", "2.1"),
            ("2.2", "2.2"),
            ("2.3", "2.3"),
            ("2.4", "2.4"),
            ("2.5", "2.5"),
            ("2.6", "2.6"),
        ]
    },
    Option.GBA_PORT_1_TYPE: {
        "default": "builtin",
        "description": ("Game Boy Advance Port 1"),
        "type": "Choice",
        "values": [
            ("builtin", N_("Built-in")),
        ]
    },
    Option.GBC_DATABASE: {
        "default": "0",
        "description": ("Enable/disable use of the Game Boy Color database"),
        "type": "Boolean",
    },
    Option.GBC_PORT_1_TYPE: {
        "default": "builtin",
        "description": ("Game Boy Color Port 1"),
        "type": "Choice",
        "values": [
            ("builtin", N_("Built-in")),
        ]
    },
    Option.GRAPHICS_CARD: {
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
    Option.GRAPHICS_MEMORY: {
        "default": "",
        "description": N_("Graphics Card RAM"),
        "type": "Choice",
        "values": [
            ("0", "0 MB"),
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
    Option.INITIAL_INPUT_GRAB: {
        "default": "",
        "description": N_("Grab Input on FS-UAE Startup"),
        "type": "boolean",
    },
    Option.IRC_NICK: {
        "default": "",
        "description": N_("IRC nickname"),
        "type": "string",
    },
    Option.IRC_SERVER: {
        "default": "irc.fs-uae.net",
        "description": N_("Custom IRC Server"),
        "type": "String",
    },
    Option.JIT_COMPILER: {
        "default": "0",
        "description": N_("JIT Compiler"),
        "type": "Boolean",
    },
    Option.JOYSTICK_PORT_0_AUTOSWITCH: {
        "default": "1",
        "description": N_("Automatic mouse/joystick mode for mouse port"),
        "type": "boolean",
    },
    Option.JOYSTICK_PORT_0_MODE: {
        "default": "mouse",
        "description": ("Joystick Port 0"),
        "type": "",
    },
    Option.JOYSTICK_PORT_1_MODE: {
        "default": "joystick",
        "description": ("Joystick Port 1"),
        "type": "",
    },
    Option.KEEP_ASPECT: {
        "default": "0",
        "description": N_("Keep aspect ratio when scaling (do not stretch)"),
        "type": "boolean",
    },
    Option.KEYBOARD_INPUT_GRAB: {
        "default": "1",
        "description": N_("Grab keyboard when input is grabbed"),
        "type": "boolean",
    },
    Option.KEYBOARD_KEY_BACKSLASH: {
        "default": "action_key_backslash",
        "description": ("Host Key BACKSLASH"),
        "type": "Choice",
        "values": [
            ("action_key_2b", "Amiga Key 0x2B"),
            ("action_key_30", "Amiga Key 0x30"),
            ("action_key_backslash", "Amiga Key Backslash"),
            ("action_key_equals", "Amiga Key Equals"),
        ]
    },
    Option.KEYBOARD_KEY_EQUALS: {
        "default": "action_key_equals",
        "description": ("Host Key EQUALS"),
        "type": "Choice",
        "values": [
            ("action_key_2b", "Amiga Key 0x2B"),
            ("action_key_30", "Amiga Key 0x30"),
            ("action_key_backslash", "Amiga Key Backslash"),
            ("action_key_equals", "Amiga Key Equals"),
        ]
    },
    Option.KEYBOARD_KEY_INSERT: {
        "default": "action_key_2b",
        "description": ("Host Key INSERT"),
        "type": "Choice",
        "values": [
            ("action_key_2b", "Amiga Key 0x2B"),
            ("action_key_30", "Amiga Key 0x30"),
            ("action_key_backslash", "Amiga Key Backslash"),
            ("action_key_equals", "Amiga Key Equals"),
        ]
    },
    Option.KEYBOARD_KEY_LESS: {
        "default": "action_key_30",
        "description": ("Host Key LESS"),
        "type": "Choice",
        "values": [
            ("action_key_2b", "Amiga Key 0x2B"),
            ("action_key_30", "Amiga Key 0x30"),
            ("action_key_backslash", "Amiga Key Backslash"),
            ("action_key_equals", "Amiga Key Equals"),
        ]
    },
    Option.KICKSTART_SETUP: {
        "default": "1",
        "description": (
            "Show kickstart setup page on startup when all ROMs are missing"),
        "type": "boolean",
    },
    Option.LAUNCHER_CLOSE_BUTTONS: {
        "default": "0",
        "description": N_("Include close buttons in dialogs"),
        "type": "Boolean",
    },
    Option.LAUNCHER_CONFIG_FEATURE: {
        "default": "0",
        "description": (
            "Experimental Config Visualization (Requires Restart)"),
        "type": "Boolean",
    },
    Option.LAUNCHER_FONT_SIZE: {
        "default": "",
        "description": N_("Launcher Font Size"),
        "type": "Integer",
        "min": 6,
        "max": 18,
    },
    Option.LAUNCHER_SETUP_WIZARD_FEATURE: {
        "default": "0",
        "description": ("Experimental Setup Wizard (Requires Restart)"),
        "type": "Boolean",
    },
    Option.LAUNCHER_THEME: {
        "default": "fusion",
        "description": N_("Launcher Theme"),
        "type": "Choice",
        "values": [
            ("standard", N_("Standard Qt Theme")),
            ("fusion", "Fusion Auto"),
            ("fusion-plain", "Fusion"),
            ("fusion-adwaita", "Fusion Adwaita"),
            ("fusion-dark", "Fusion Dark"),
            ("fusion-windows10", "Fusion Windows 10"),
        ]
    },
    Option.LOAD_STATE: {
        "default": "",
        "description": ("Load state by number"),
        "type": "integer",
        "min": 1,
        "max": 9,
    },
    Option.LOG_AUTOSCALE: {
        "default": "0",
        "description": N_("Log Autoscale Changes"),
        "type": "boolean",
    },
    Option.LOG_BSDSOCKET: {
        "default": "0",
        "description": "",
        "type": "boolean",
    },
    Option.LOG_FLUSH: {
        "default": "",
        "description": ("Flush log after each log line"),
        "type": "boolean",
    },
    Option.LOG_INPUT: {
        "default": "0",
        "description": N_("Log Input Events"),
        "type": "boolean",
    },
    Option.LOG_QUERY_PLANS: {
        "default": "",
        "description": ("Log database query plans"),
        "type": "",
    },
    Option.LOW_LATENCY_VSYNC: {
        "default": "1",
        "description": N_("Low latency video sync"),
        "type": "boolean",
    },
    Option.MAME_ARTWORK: {
        "default": "0",
        "description": ("Use MAME Artwork"),
        "type": "Boolean",
    },
    Option.MEDNAFEN_AUDIO_BUFFER: {
        "default": "40",
        "description": ("Mednafen Audio Buffer"),
        "type": "Integer",
        "min": 0,
        "max": 1000,
    },
    Option.MEDNAFEN_AUDIO_DRIVER: {
        "default": "auto",
        "description": ("Mednafen Audio Driver"),
        "type": "Choice",
        "values": [
            ("auto", "Auto"),
            ("sdl", "SDL"),
            ("alsa", "ALSA"),
            ("mednafen", "Mednafen Default"),
        ]
    },
    Option.MIDDLE_CLICK_UNGRAB: {
        "default": "1",
        "description": N_("Ungrab Input on Middle Mouse Button"),
        "type": "boolean",
    },
    Option.MIN_FIRST_LINE_NTSC: {
        "default": "21",
        "description": ("First rendered line (NTSC)"),
        "type": "",
    },
    Option.MIN_FIRST_LINE_PAL: {
        "default": "26",
        "description": ("First rendered line (PAL)"),
        "type": "",
    },
    Option.MONITOR: {
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
    Option.MOTHERBOARD_RAM: {
        "default": "",
        "description": ("Motherboard RAM"),
        "type": "Choice",
        "values": [
            ("0", "0 MB"),
            ("1024", "1 MB"),
            ("2048", "2 MB"),
            ("4096", "4 MB"),
            ("8192", "8 MB"),
            ("16384", "16 MB"),
            ("32768", "32 MB"),
            ("65536", "64 MB"),
        ]
    },
    Option.MOUSE_SPEED: {
        "default": "100",
        "description": N_("Mouse Speed (%)"),
        "type": "integer",
        "min": 1,
        "max": 500,
    },
    Option.MSX_DATABASE: {
        "default": "0",
        "description": ("Enable/disable use of the MSX game database"),
        "type": "Boolean",
    },
    Option.N64_DATABASE: {
        "default": "0",
        "description": ("Enable/disable use of the Nintendo 64 database"),
        "type": "Boolean",
    },
    Option.NDS_DATABASE: {
        "default": "0",
        "description": ("Enable/disable use of the Nintendo DS database"),
        "type": "Boolean",
    },
    Option.NEOGEO_DATABASE: {
        "default": "0",
        "description": ("Enable/disable use of the Neo-Geo game database"),
        "type": "Boolean",
    },
    Option.NEOGEO_MODEL: {
        "default": "mvs",
        "description": ("Neo-Geo Model"),
        "type": "Choice",
        "values": [
            ("mvs", "MVS Europe"),
            ("mvs/jp", "MVS Japan"),
            ("mvs/us", "MVS US"),
            ("aes", "AES"),
            ("aes/jp", "AES Japan"),
        ]
    },
    Option.NEOGEO_PORT_1_TYPE: {
        "default": "joystick",
        "description": ("Neo-Geo Port 1"),
        "type": "Choice",
        "values": [
            ("none", N_("None")),
            ("joystick", N_("Joystick")),
        ]
    },
    Option.NEOGEO_PORT_2_TYPE: {
        "default": "joystick",
        "description": ("Neo-Geo Port 2"),
        "type": "Choice",
        "values": [
            ("none", N_("None")),
            ("joystick", N_("Joystick")),
        ]
    },
    Option.NES_DATABASE: {
        "default": "0",
        "description": ("Enable/disable use of the Nintendo (NES) database"),
        "type": "Boolean",
    },
    Option.NES_DRIVER: {
        "default": "mednafen",
        "description": ("NES Game Driver"),
        "type": "Choice",
        "values": [
            ("mednafen-fs", "Mednafen-FS"),
            ("higan", "Higan"),
            ("libretro-nestopia", "Nestopia (RetroArch)"),
            ("mednafen", "mednafen"),
            ("mess", "mess"),
        ]
    },
    Option.NES_EMULATOR: {
        "default": "mednafen",
        "description": ("Nintendo Emulator"),
        "type": "Choice",
        "values": [
            ("mednafen", "Mednafen"),
            ("higan", "Higan"),
            ("retroarch-nestopia", "RetroArch Nestopia"),
        ]
    },
    Option.NES_MODEL: {
        "default": "ntsc",
        "description": ("NES Model"),
        "type": "Choice",
        "values": [
            ("ntsc", "NES NTSC"),
            ("pal", "NES PAL"),
            ("ntsc-j", "Famicom"),
        ]
    },
    Option.NES_PORT_1_TYPE: {
        "default": "gamepad",
        "description": ("NES Port 1"),
        "type": "Choice",
        "values": [
            ("none", N_("None")),
            ("gamepad", N_("Gamepad")),
            ("zapper", "Zapper"),
            ("arkanoid", "Arkanoid"),
        ]
    },
    Option.NES_PORT_2_TYPE: {
        "default": "gamepad",
        "description": ("NES Port 2"),
        "type": "Choice",
        "values": [
            ("none", N_("None")),
            ("gamepad", N_("Gamepad")),
            ("zapper", "Zapper"),
            ("arkanoid", "Arkanoid"),
        ]
    },
    Option.NES_PORT_3_TYPE: {
        "default": "none",
        "description": ("NES Port 3"),
        "type": "Choice",
        "values": [
            ("none", N_("None")),
            ("gamepad", N_("Gamepad")),
        ]
    },
    Option.NES_PORT_4_TYPE: {
        "default": "none",
        "description": ("NES Port 4"),
        "type": "Choice",
        "values": [
            ("none", N_("None")),
            ("gamepad", N_("Gamepad")),
        ]
    },
    Option.NETPLAY_FEATURE: {
        "default": "0",
        "description": (
            "Enable experimental net play GUI (requires restart)"),
        "type": "boolean",
    },
    Option.NETPLAY_TAG: {
        "default": "UNK",
        "description": N_("Net play tag (max 3 characters)"),
        "type": "string",
    },
    Option.NETWORK_CARD: {
        "default": "0",
        "description": N_("Network Card"),
        "type": "Choice",
        "values": [
            ("0", N_("None")),
            ("a2065", "A2065"),
        ]
    },
    Option.NGC_DATABASE: {
        "default": "0",
        "description": ("Enable/disable use of the GameCube database"),
        "type": "Boolean",
    },
    Option.PLATFORM: {
        "default": "amiga",
        "description": ("Platform"),
        "type": "Choice",
        "values": [
            ("amiga", "Amiga"),
            ("cpc", "Amstrad CPC"),
            ("a2600", "Atari 2600"),
            ("a5200", "Atari 5200"),
            ("a7800", "Atari 7800"),
            ("atari", "Atari ST"),
            ("arcade", "Arcade"),
            ("cd32", "CD32"),
            ("cdtv", "CDTV"),
            ("c64", "Commodore 64"),
            ("dos", "DOS"),
            ("gb", "Game Boy"),
            ("gba", "Game Boy Advance"),
            ("gbc", "Game Boy Color"),
            ("ngc", "GameCube"),
            ("neogeo", "Neo-Geo"),
            ("nes", "Nintendo"),
            ("n64", "Nintendo 64"),
            ("nds", "Nintendo DS"),
            ("sms", "Master System"),
            ("smd", "Mega Drive"),
            ("psx", "PlayStation"),
            ("snes", "Super Nintendo"),
            ("tg16", "TurboGrafx-16"),
            ("tgcd", "TurboGrafx-CD"),
            ("zxs", "ZX Spectrum"),
        ]
    },
    Option.PLATFORMS_FEATURE: {
        "default": "0",
        "description": N_("Enable Additional Platforms (Requires Restart)"),
        "type": "Boolean",
    },
    Option.PSX_DATABASE: {
        "default": "0",
        "description": ("Enable/disable use of the PlayStation database"),
        "type": "Boolean",
    },
    Option.PSX_MODEL: {
        "default": "ntsc",
        "description": ("PlayStation Model"),
        "type": "Choice",
        "values": [
            ("ntsc", "NTSC v3.0A ROM BIOS"),
            ("ntsc-j", "NTSC-J v3.0J ROM BIOS"),
            ("pal", "PAL v3.0E ROM BIOS"),
        ]
    },
    Option.PSX_PORT_1_TYPE: {
        "default": "gamepad",
        "description": ("PlayStation Port 1"),
        "type": "Choice",
        "values": [
            ("none", N_("None")),
            ("gamepad", N_("Gamepad")),
        ]
    },
    Option.PSX_PORT_2_TYPE: {
        "default": "gamepad",
        "description": ("PlayStation Port 1"),
        "type": "Choice",
        "values": [
            ("none", N_("None")),
            ("gamepad", N_("Gamepad")),
        ]
    },
    Option.PSX_PRELOAD: {
        "default": "0",
        "description": ("Preload PlayStation CD images in RAM"),
        "type": "Boolean",
    },
    Option.QUICK_SETTINGS_OPTIONS: {
        "default": "",
        "description": ("Quick Settings to Display"),
        "type": "String",
    },
    Option.RAW_INPUT: {
        "default": "1",
        "description": N_("Use keyboard raw input (Windows)"),
        "type": "Boolean",
    },
    Option.RELATIVE_PATHS: {
        "default": "",
        "description": ("Relative paths"),
        "type": "",
    },
    Option.RELATIVE_TEMP_FEATURE: {
        "default": "0",
        "description": ("Relative Temporary Directories"),
        "type": "Boolean",
    },
    Option.RETROARCH_AUDIO_BUFFER: {
        "default": "40",
        "description": ("RetroArch Audio Buffer"),
        "type": "Integer",
        "min": 0,
        "max": 1000,
    },
    Option.RTG_SCANLINES: {
        "default": "0",
        "description": N_("Render scan lines in RTG graphics mode"),
        "type": "boolean",
    },
    Option.SAVE_DISK: {
        "default": "1",
        "description": ("Save Disk"),
        "type": "Boolean",
    },
    Option.SCALE: {
        "default": "1",
        "description": ("Scale"),
        "type": "Choice",
        "values": [
            ("1", N_("Max Scaling")),
            ("0", N_("No Scaling")),
            ("integer", N_("Integer Scaling")),
            ("legacy", N_("Legacy Scaling")),
        ]
    },
    Option.SCANLINES: {
        "default": "0",
        "description": N_("Render scan lines"),
        "type": "boolean",
    },
    Option.SLOW_MEMORY: {
        "default": "",
        "description": N_("Slow RAM"),
        "type": "Choice",
        "values": [
            ("0", "0 MB"),
            ("512", "512 KB"),
            ("1024", "1 MB"),
            ("1536", "1.5 MB"),
            ("1792", "1.8 MB"),
        ]
    },
    Option.SMD_DATABASE: {
        "default": "0",
        "description": (
            "Enable/disable use of the Sega Mega Drive (Genesis) database"),
        "type": "Boolean",
    },
    Option.SMD_EMULATOR: {
        "default": "mednafen-fs",
        "description": ("Mega Drive Emulator"),
        "type": "Choice",
        "values": [
            ("mame-fs", "MAME-FS"),
            ("mednafen", "Mednafen"),
            ("mednafen-fs", "Mednafen-FS"),
            ("retroarch-fs", "RetroArch-FS"),
            ("retroarch-fs/genesisplusgx", "RetroArch-FS: Genesis Plus GX"),
        ]
    },
    Option.SMD_MODEL: {
        "default": "ntsc",
        "description": ("Mega Drive Model"),
        "type": "Choice",
        "values": [
            ("ntsc", "Genesis"),
            ("pal", "Mega Drive PAL"),
            ("ntsc-j", "Mega Drive NTSC-J"),
        ]
    },
    Option.SMD_PORT_1_TYPE: {
        "default": "gamepad",
        "description": ("Mega Drive Port 1"),
        "type": "Choice",
        "values": [
            ("none", N_("None")),
            ("gamepad", "Control Pad"),
            ("gamepad6", N_("Six Button Control Pad")),
        ]
    },
    Option.SMD_PORT_2_TYPE: {
        "default": "gamepad",
        "description": ("Mega Drive Port 2"),
        "type": "Choice",
        "values": [
            ("none", N_("None")),
            ("gamepad", "Control Pad"),
            ("gamepad6", N_("Six Button Control Pad")),
        ]
    },
    Option.SMOOTHING: {
        "default": "auto",
        "description": ("Smoothing"),
        "type": "Choice",
        "values": [
            ("auto", N_("Auto Smoothing")),
            ("0", N_("No Smoothing")),
            ("1", N_("Smoothing")),
        ]
    },
    Option.SMS_DATABASE: {
        "default": "0",
        "description": (
            "Enable/disable use of the Sega Master System database"),
        "type": "Boolean",
    },
    Option.SMS_DRIVER: {
        "default": "mednafen",
        "description": ("Master System Game Driver"),
        "type": "Choice",
        "values": [
            ("mednafen", "mednafen"),
            ("mess", "mess"),
        ]
    },
    Option.SNES_DATABASE: {
        "default": "0",
        "description": ("Enable/disable use of the Super Nintendo database"),
        "type": "Boolean",
    },
    Option.SNES_PORT_1_TYPE: {
        "default": "gamepad",
        "description": ("SNES Port 1"),
        "type": "Choice",
        "values": [
            ("none", N_("None")),
            ("gamepad", N_("Gamepad")),
        ]
    },
    Option.SNES_PORT_2_TYPE: {
        "default": "gamepad",
        "description": ("SNES Port 2"),
        "type": "Choice",
        "values": [
            ("none", N_("None")),
            ("gamepad", N_("Gamepad")),
        ]
    },
    Option.SOUND_CARD: {
        "default": "0",
        "description": N_("Sound Card"),
        "type": "Choice",
        "values": [
            ("0", N_("None")),
            ("toccata", "Toccata"),
        ]
    },
    Option.STEREO_SEPARATION: {
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
    Option.STRETCH: {
        "default": "aspect",
        "description": ("Stretch"),
        "type": "Choice",
        "values": [
            ("1", N_("Fill Screen")),
            ("aspect", N_("Correct Aspect")),
            ("0", N_("Square Pixels")),
        ]
    },
    Option.SWAP_CTRL_KEYS: {
        "default": "0",
        "description": N_("Swap left and right CTRL keys"),
        "type": "boolean",
    },
    Option.TEXTURE_FILTER: {
        "default": "linear",
        "description": N_("Texture filter"),
        "type": "choice",
        "values": [
            ("nearest", "GL_NEAREST"),
            ("linear", "GL_LINEAR"),
        ]
    },
    Option.TEXTURE_FORMAT: {
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
    Option.TG16_DATABASE: {
        "default": "0",
        "description": (
            "Enable/disable use of the TurboGrafx-16 game database"),
        "type": "Boolean",
    },
    Option.TGCD_DATABASE: {
        "default": "0",
        "description": (
            "Enable/disable use of the TurboGrafx-CD game database"),
        "type": "Boolean",
    },
    Option.TURBO_LOAD: {
        "default": "1",
        "description": ("Turbo Load"),
        "type": "Boolean",
    },
    Option.UAE_A2065: {
        "default": "",
        "description": "uae_a2065",
        "type": "",
        "values": [
            ("slirp", "slirp"),
        ]
    },
    Option.UAE_A3000MEM_SIZE: {
        "default": "",
        "description": "Size in megabytes of motherboard fast memory",
        "type": "integer",
        "min": 0,
        "max": 65536,
    },
    Option.UAE_CHIPSET_COMPATIBLE: {
        "default": "",
        "description":
            "Enable default chipset features for a specific model",
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
    Option.UAE_CPU_FREQUENCY: {
        "default": "",
        "description":
            "Specify the frequency of the emulated CPU in cycle-exact modes",
        "type": "float",
        "min": 1.0,
        "max": 100.0,
    },
    Option.UAE_CPU_MULTIPLIER: {
        "default": "",
        "description": "FIXME",
        "type": "integer",
        "min": 0,
        "max": 256,
    },
    Option.UAE_CPU_SPEED: {
        "default": "",
        "description": "Enable/disable fastest possible CPU speed",
        "type": "choice",
        "values": [
            ("real", "Approximate A500/A1200 or cycle-exact"),
            ("max", "Fastest possible"),
        ]
    },
    Option.UAE_CPU_THROTTLE: {
        "default": "",
        "description": "FIXME",
        "type": "float",
        "min": -900.0,
        "max": 5000.0,
    },
    Option.UAE_FASTMEM2_SIZE: {
        "default": "0",
        "description":
            "Size in MB of Zorro-II Fast RAM (second) expansion board",
        "type": "choice",
        "values": [
            ("0", "0"),
            ("1", "1"),
            ("2", "2"),
            ("4", "4"),
        ]
    },
    Option.UAE_FASTMEM_AUTOCONFIG: {
        "default": "1",
        "description": "Autoconfig Z2 Fast RAM",
        "type": "boolean",
    },
    Option.UAE_FASTMEM_SIZE: {
        "default": "0",
        "description": "Size in MB of Zorro-II Fast RAM expansion board",
        "type": "choice",
        "values": [
            ("0", "0"),
            ("1", "1"),
            ("2", "2"),
            ("4", "4"),
            ("8", "8"),
        ]
    },
    Option.UAE_FORCE_0X10000000_Z3: {
        "default": "false",
        "description": "Force Zorro-III address space at 0x10000000",
        "type": "boolean",
    },
    Option.UAE_GFX_LINEMODE: {
        "default": "",
        "description":
            "Controls how lines are doubled and interlaced modes are handled",
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
    Option.UAE_MBRESMEM_SIZE: {
        "default": "",
        "description": "Size in megabytes of processor slot fast memory",
        "type": "integer",
        "min": 0,
        "max": 131072,
    },
    Option.UAE_RTC: {
        "default": "auto",
        "description": "Enable a real time clock (RTC) module.",
        "type": "Choice",
        "values": [
            ("auto", "Auto"),
            ("none", "None"),
            ("MSM6242B", "Oki MSM6242B"),
            ("RP5C01A", "Ricoh RP5C01A"),
            ("MSM6242B_A2000", "A2000 MSM6242B"),
        ]
    },
    Option.UAE_SANA2: {
        "default": "false",
        "description": "uae_sana2",
        "type": "BooleanUAE,",
    },
    Option.UAE_SLIRP_IMPLEMENTATION: {
        "default": "auto",
        "description": "Slirp Implementation",
        "type": "Choice",
        "values": [
            ("auto", "auto"),
            ("none", "none"),
            ("builtin", "builtin"),
            ("qemu", "qemu"),
        ]
    },
    Option.UAE_SOUND_OUTPUT: {
        "default": "",
        "description": "Sound emulation",
        "type": "",
        "values": [
            ("none", "Disabled"),
            ("interrupts", "Emulated, No Output"),
            ("exact", "Enabled"),
        ]
    },
    Option.UAE_TOCCATA: {
        "default": "",
        "description": "Toccata Z2 sound card emulation",
        "type": "uaeyesno",
    },
    Option.UAE_Z3CHIPMEM_SIZE: {
        "default": "",
        "description": "",
        "type": "integer",
    },
    Option.UAE_Z3MAPPING: {
        "default": "auto",
        "description": "JIT Direct compatible Z3 memory mapping",
        "type": "choice",
    },
    Option.UAE_Z3MEM2_SIZE: {
        "default": "",
        "description": "",
        "type": "integer",
    },
    Option.UAE_Z3MEM_SIZE: {
        "default": "",
        "description": "Size in MB of Zorro-III Fast RAM expansion board",
        "type": "integer",
    },
    Option.UAEGFX_CARD: {
        "default": "0",
        "description": ("Deprecated: uaegfx_card"),
        "type": "boolean",
    },
    Option.UAEM_WRITE_FLAGS: {
        "default": "1",
        "description": ("Write .uaem metadata files"),
        "type": "flags",
    },
    Option.VICE_AUDIO_DRIVER: {
        "default": "auto",
        "description": ("Vice Audio Driver"),
        "type": "Choice",
        "values": [
            ("auto", N_("Auto")),
            ("sdl", "SDL"),
        ]
    },
    Option.VIDEO_FORMAT: {
        "default": "bgra",
        "description": N_("Video buffer format and color depth"),
        "type": "choice",
        "values": [
            ("bgra", N_("32-bit BGRA")),
            ("rgba", N_("32-bit RGBA")),
            ("rgb565", N_("16-bit")),
        ]
    },
    Option.VIDEO_SYNC: {
        "default": "0",
        "description": N_("Video synchronization"),
        "type": "choice",
        "values": [
            ("1", N_("Auto")),
            ("0", N_("Off")),
        ]
    },
    Option.VIDEO_SYNC_METHOD: {
        "default": "auto",
        "description": N_("Video synchronization method"),
        "type": "choice",
        "values": [
            ("auto", "Auto"),
            ("swap", "Swap"),
            ("swap-finish", "Swap-Finish"),
            ("finish-swap-finish", "Finish-Swap-Finish"),
            ("finish-sleep-swap-finish", "Finish-Sleep-Swap-Finish"),
            ("sleep-swap-finish", "Sleep-Swap-Finish"),
            ("swap-fence", "Swap-Fence"),
            ("swap-sleep-fence", "Swap-Sleep-Fence"),
        ]
    },
    Option.VOLUME: {
        "default": "100",
        "description": N_("Main Volume"),
        "type": "integer",
        "min": 0,
        "max": 100,
    },
    Option.WARP_MODE: {
        "default": "0",
        "description": ("Start in warp mode"),
        "type": "Boolean",
    },
    Option.WHDLOAD_BOOT_DIR: {
        "default": "",
        "description": (
            "Custom boot directory for automatic WHDLoad support"),
        "type": "",
    },
    Option.WHDLOAD_MODEL: {
        "default": "auto",
        "description": ("Override WHDLoad Amiga model"),
        "type": "Choice",
        "values": [
            ("0", "No override"),
            ("A1200", "A1200"),
            ("A1200/NONCE", "A1200/NONCE"),
        ]
    },
    Option.WHDLOAD_PRELOAD: {
        "default": "1",
        "description": N_("Override WHDLoad preload option"),
        "type": "Boolean",
    },
    Option.WHDLOAD_QUIT_KEY: {
        "default": "0",
        "description": N_("Override WHDLoad quit key"),
        "type": "Choice",
        "values": [
            ("0", "No override"),
            ("$45", "Escape"),
            ("$50", "F1"),
            ("$51", "F2"),
            ("$52", "F3"),
            ("$53", "F4"),
            ("$54", "F5"),
            ("$55", "F6"),
            ("$56", "F7"),
            ("$57", "F8"),
            ("$58", "F9"),
            ("$59", "F10"),
        ]
    },
    Option.WHDLOAD_SPLASH_DELAY: {
        "default": "200",
        "description": N_("Override WHDLoad splash delay"),
        "type": "integer",
        "min": -1,
        "max": 500,
    },
    Option.WINDOW_BORDER: {
        "default": "",
        "description": ("Show window border and decorations"),
        "type": "boolean",
    },
    Option.WINDOW_HIDDEN: {
        "default": "0",
        "description": ("Window is hidden on startup"),
        "type": "Boolean",
    },
    Option.WINDOW_MINIMIZED: {
        "default": "0",
        "description": ("Window is minimized on startup"),
        "type": "Boolean",
    },
    Option.ZOOM: {
        "default": "692x540",
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
            ("692x540", "692x540"),
            ("704x540", "704x540"),
            ("704x566", "704x566"),
            ("724x566", "724x566"),
        ]
    },
    Option.ZORRO_III_MEMORY: {
        "default": "",
        "description": N_("Zorro III Fast Memory"),
        "type": "Choice",
        "values": [
            ("0", "0 MB"),
            ("1024", "1 MB"),
            ("2048", "2 MB"),
            ("4096", "4 MB"),
            ("8192", "8 MB"),
            ("16384", "16 MB"),
            ("32768", "32 MB"),
            ("65536", "64 MB"),
            ("131072", "128 MB"),
            ("262144", "256 MB"),
            ("393216", "384 MB"),
            ("524288", "512 MB"),
            ("786432", "768 MB"),
            ("1048576", "1024 MB"),
        ]
    },
    Option.ZXS_DATABASE: {
        "default": "0",
        "description": ("Enable/disable use of the ZX Spectrum database"),
        "type": "Boolean",
    },
    Option.ZXS_DRIVER: {
        "default": "fuse",
        "description": ("ZX Spectrum Game Driver"),
        "type": "Choice",
        "values": [
            ("fuse", "Fuse"),
            ("mess", "MESS"),
        ]
    },
    Option.ZXS_MODEL: {
        "default": "spectrum",
        "description": ("ZX Spectrum Model"),
        "type": "Choice",
        "values": [
            ("spectrum", "Spectrum 48K"),
            ("spectrum/if2", "Spectrum 48K, Interface 2"),
            ("spectrum128", "Spectrum 128"),
            ("spectrum+3", "Spectrum +3"),
        ]
    },
}
