from .roms import *


class Amiga(object):

    # FIXME: setting fake checksum, for now
    INTERNAL_ROM_SHA1 = "0000000000000000000000000000000000000000"

    MAX_FLOPPY_DRIVES = 4
    MAX_FLOPPY_IMAGES = 20
    MAX_CDROM_DRIVES = 4
    MAX_CDROM_IMAGES = 20
    MAX_HARD_DRIVES = 4

    models = [
        {
            "title": "Amiga 500",
            "cd_based": False,
            "kickstarts": A500_KICKSTARTS,
            "ext_roms": [],
            "defaults": {
                "chip_memory": "512",
                "slow_memory": "512",
                "fast_memory": "0",
                "zorro_iii_memory": "0",
            }
        }, {
            "title": "Amiga 500 (512K)",
            "cd_based": False,
            "kickstarts": A500_KICKSTARTS,
            "ext_roms": [],
            "defaults": {
                "chip_memory": "512",
                "slow_memory": "0",
                "fast_memory": "0",
                "zorro_iii_memory": "0",
            }
        }, {
            "title": "Amiga 500+",
            "cd_based": False,
            "kickstarts": A500P_KICKSTARTS,
            "ext_roms": [],
            "defaults": {
                "chip_memory": "1024",
                "slow_memory": "0",
                "fast_memory": "0",
                "zorro_iii_memory": "0",
            }
        }, {
            "title": "Amiga 600",
            "cd_based": False,
            "kickstarts": A600_KICKSTARTS,
            "ext_roms": [],
            "defaults": {
                "chip_memory": "1024",
                "slow_memory": "0",
                "fast_memory": "0",
                "zorro_iii_memory": "0",
            }
        }, {
            "title": "Amiga 1000",
            "cd_based": False,
            "kickstarts": A1000_KICKSTARTS,
            "ext_roms": [],
            "defaults": {
                "chip_memory": "512",
                "slow_memory": "0",
                "fast_memory": "0",
                "zorro_iii_memory": "0",
            }
        }, {
            "title": "Amiga 1200",
            "cd_based": False,
            "kickstarts": A1200_KICKSTARTS,
            "ext_roms": [],
            "defaults": {
                "chip_memory": "2048",
                "slow_memory": "0",
                "fast_memory": "0",
                "zorro_iii_memory": "0",
            }
        }, {
            "title": "Amiga 1200 (68020)",
            "cd_based": False,
            "kickstarts": A1200_KICKSTARTS,
            "ext_roms": [],
            "defaults": {
                "chip_memory": "2048",
                "slow_memory": "0",
                "fast_memory": "0",
                "zorro_iii_memory": "0",
            }
        }, {
            "title": "Amiga 3000",
            "cd_based": False,
            "kickstarts": A3000_KICKSTARTS,
            "ext_roms": [],
            "defaults": {
                "chip_memory": "1024",
                "slow_memory": "0",
                "fast_memory": "0",
                "zorro_iii_memory": "0",
            }
        }, {
            "title": "Amiga 4000",
            "cd_based": False,
            "kickstarts": A4000_KICKSTARTS,
            "ext_roms": [],
            "defaults": {
                "chip_memory": "2048",
                "slow_memory": "0",
                "fast_memory": "0",
                "zorro_iii_memory": "0",
            }
        }, {
            "title": "Amiga 4000 (68040)",
            "cd_based": False,
            "kickstarts": A4000_KICKSTARTS,
            "ext_roms": [],
            "defaults": {
                "chip_memory": "2048",
                "slow_memory": "0",
                "fast_memory": "0",
                "zorro_iii_memory": "0",
            }
        }, {
            "title": "Amiga 4000 (PPC)",
            "cd_based": False,
            "kickstarts": A4000_KICKSTARTS,
            "ext_roms": [],
            "defaults": {
                "chip_memory": "2048",
                "slow_memory": "0",
                "fast_memory": "0",
                "zorro_iii_memory": "0",
                "accelerator": "cyberstorm-ppc",
            }
        }, {
            "title": "Amiga 4000 (PPC / OS4)",
            "cd_based": False,
            "kickstarts": A4000_KICKSTARTS,
            "ext_roms": [],
            "defaults": {
                "chip_memory": "2048",
                "slow_memory": "0",
                "fast_memory": "0",
                "zorro_iii_memory": "0",
                "accelerator": "cyberstorm-ppc",
                "graphics_card": "picasso-iv-z3"
            }
        }, {
            "title": "Amiga CD32",
            "cd_based": "CD32",
            "kickstarts": CD32_KICKSTARTS,
            "ext_roms": CD32_EXT_ROMS,
            "defaults": {
                "chip_memory": "2048",
                "slow_memory": "0",
                "fast_memory": "0",
                "zorro_iii_memory": "0",
            }
        }, {
            "title": "Amiga CD32 + FMV ROM",
            "cd_based": "CD32",
            "kickstarts": CD32_KICKSTARTS,
            "ext_roms": CD32_EXT_ROMS,
            "defaults": {
                "chip_memory": "2048",
                "slow_memory": "0",
                "fast_memory": "0",
                "zorro_iii_memory": "0",
            }
        }, {
            "title": "Commodore CDTV",
            "cd_based": "CDTV",
            "kickstarts": CDTV_KICKSTARTS,
            "ext_roms": CDTV_EXT_ROMS,
            "defaults": {
                "chip_memory": "1024",
                "slow_memory": "0",
                "fast_memory": "0",
                "zorro_iii_memory": "0",
            }
        }
    ]

    models_config = [
        "A500",
        "A500/512K",
        "A500+",
        "A600",
        "A1000",
        "A1200",
        "A1200/020",
        "A3000",
        "A4000",
        "A4000/040",
        "A4000/PPC",
        "A4000/OS4",
        "CD32",
        "CD32/FMV",
        "CDTV",
    ]

    @classmethod
    def is_cd_based(cls, Config):
        return cls.get_current_config(Config)["cd_based"]

    @classmethod
    def get_current_config(cls, Config):
        return cls.get_model_config(Config.get("amiga_model"))

    @classmethod
    def get_default_option_value(cls, model, key):
        model = model.upper()
        if not model:
            model = "A500"
        return cls.get_model_config(model)["defaults"].get(key, "")

    @classmethod
    def get_model_config(cls, model):
        model = model.upper()
        if not model:
            model = "A500"
        for i in range(len(cls.models_config)):
            if cls.models_config[i].upper() == model:
                return cls.models[i]
        return {
            "title": "Dummy",
            "cd_based": False,
            "kickstarts": [
            ],
            "ext_roms": [
            ],
            "defaults": {
                "chip_memory": "0",
                "slow_memory": "0",
                "fast_memory": "0",
                "zorro_iii_memory": "0",
            }
        }
