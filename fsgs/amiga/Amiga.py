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
            "id": "A1000",
            "title": "A1000",
            "subtitle": "1.2 ROM, 512 KB Chip RAM",
            "cd_based": False,
            "kickstarts": A1000_KICKSTARTS,
            "ext_roms": [],
            "defaults": {
            }
        },
        {
            "id": "A500/512K",
            "title": "Amiga 500 (512K)",
            # "subtitle": "1.3 ROM, 512 KB Chip RAM",
            "subtitle": "1.3 ROM",
            "cd_based": False,
            "kickstarts": A500_KICKSTARTS,
            "ext_roms": [],
            "defaults": {
            }
        },
        {
            "id": "A500",
            "title": "A500",
            # "subtitle": "1.3 ROM, 512 KB Chip  + 512 KB Slow RAM",
            # "subtitle": "1.3 ROM, 512 KB RAM Trapdoor Expansion",
            "subtitle": "1.3 ROM, 512 KB \"Slow\" RAM",
            # "subtitle": "1.3 ROM, 512 KB  RAM",
            "cd_based": False,
            "kickstarts": A500_KICKSTARTS,
            # "kickstarts": ["0123456789012345678901234567890123456789"],
            "ext_roms": [],
            "defaults": {
            }
        },
        {
            "id": "A500+",
            "title": "A500+",
            "subtitle": "2.04 ROM",
            "cd_based": False,
            "kickstarts": A500P_KICKSTARTS,
            "ext_roms": [],
            "defaults": {
            }
        },
        {
            "id": "A600",
            "title": "A600",
            "subtitle": "2.05 ROM",
            "cd_based": False,
            "kickstarts": A600_KICKSTARTS,
            "ext_roms": [],
            "defaults": {
            }
        },
        {
            "id": "A1200/3.0",
            "title": "A1200",
            "subtitle": "3.0 ROM",
            "cd_based": False,
            "kickstarts": A1200_3_0_KICKSTARTS,
            "ext_roms": [],
            "defaults": {
            }
        },
        {
            "id": "A1200",
            "title": "A1200",
            "subtitle": "3.1 ROM",
            "cd_based": False,
            "kickstarts": A1200_3_1_KICKSTARTS,
            "ext_roms": [],
            "defaults": {
            }
        },
        {
            "id": "A1200/020",
            "title": "Amiga 1200 (68020)",
            "subtitle": "3.1 ROM, 68020 CPU",
            "cd_based": False,
            "kickstarts": A1200_3_1_KICKSTARTS,
            "ext_roms": [],
            "defaults": {
            }
        },
        {
            "id": "A1200/1230",
            "title": "A1200",
            "subtitle": "3.1 ROM, Blizzard 1230 IV",
            "cd_based": False,
            "kickstarts": A1200_3_1_KICKSTARTS,
            "ext_roms": [],
            "defaults": {
            }
        },
        {
            "id": "A1200/1240",
            "title": "A1200",
            "subtitle": "3.1 ROM, Blizzard 1240",
            "cd_based": False,
            "kickstarts": A1200_3_1_KICKSTARTS,
            "ext_roms": [],
            "defaults": {
            }
        },
        {
            "id": "A1200/1260",
            "title": "A1200",
            "subtitle": "3.1 ROM, Blizzard 1260",
            "cd_based": False,
            "kickstarts": A1200_3_1_KICKSTARTS,
            "ext_roms": [],
            "defaults": {
            }
        },
        {
            "id": "A1200/PPC",
            "title": "A1200",
            "subtitle": "3.1 ROM, Blizzard PPC",
            "cd_based": False,
            "kickstarts": A1200_3_1_KICKSTARTS,
            "ext_roms": [],
            "defaults": {
            }
        },
        {
            "id": "A3000",
            "title": "A3000",
            "subtitle": "3.1 ROM, 2 MB Chip + 8 MB Fast RAM",
            "cd_based": False,
            "kickstarts": A3000_KICKSTARTS,
            "ext_roms": [],
            "defaults": {
            }
        },
        {
            "id": "A4000",
            "title": "A4000",
            "subtitle": "3.1 ROM",
            "cd_based": False,
            "kickstarts": A4000_KICKSTARTS,
            "ext_roms": [],
            "defaults": {
            }
        },
        {
            "id": "A4000/040",
            "title": "Amiga 4000 (68040)",
            "subtitle": "3.1 ROM, 68040 CPU",
            "cd_based": False,
            "kickstarts": A4000_KICKSTARTS,
            "ext_roms": [],
            "defaults": {
            }
        },
        {
            "id": "A4000/PPC",
            "title": "Amiga 4000 (PPC)",
            "subtitle": "3.1 ROM, CyberStorm PPC",
            "cd_based": False,
            "kickstarts": A4000_KICKSTARTS,
            "ext_roms": [],
            "defaults": {
                "accelerator": "cyberstorm-ppc",
            }
        },
        {
            "id": "A4000/OS4",
            "title": "Amiga 4000 (PPC / OS4)",
            "subtitle": "3.1 ROM, CyberStorm PPC (AmigaOS 4.x)",
            "cd_based": False,
            "kickstarts": A4000_KICKSTARTS,
            "ext_roms": [],
            "defaults": {
                "accelerator": "cyberstorm-ppc",
                "graphics_card": "picasso-iv-z3"
            }
        },
        {
            "id": "CD32",
            "title": "CD32",
            "subtitle": "3.1 ROM",
            "cd_based": "CD32",
            "kickstarts": CD32_KICKSTARTS,
            "ext_roms": CD32_EXT_ROMS,
            "defaults": {
            }
        },
        {
            "id": "CD32/FMV",
            "title": "CD32 + FMV ROM",
            "subtitle": "3.1 ROM, FMV Expansion (ROM)",
            "cd_based": "CD32",
            "kickstarts": CD32_KICKSTARTS,
            "ext_roms": CD32_EXT_ROMS,
            "defaults": {
            }
        },
        {
            "id": "CDTV",
            "title": "CDTV",
            "subtitle": "1.3 ROM",
            "cd_based": "CDTV",
            "kickstarts": CDTV_KICKSTARTS,
            "ext_roms": CDTV_EXT_ROMS,
            "defaults": {
            }
        }
    ]

    models_config = [model["id"] for model in models]

    @classmethod
    def is_cd_based(cls, config):
        return cls.get_current_config(config)["cd_based"]

    @classmethod
    def get_current_config(cls, config):
        return cls.get_model_config(config.get("amiga_model"))

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
