# Automatically generated - do not edit by hand


# noinspection PyUnusedLocal,SpellCheckingInspection,PyUnresolvedReferences
def _accelerator(c, f):
    if c.accelerator.explicit:
        value = c.accelerator.explicit
    elif c.amiga_model == "A1200/1230":
        value = "blizzard-1230-iv"
    elif c.amiga_model == "A1200/1240":
        value = "blizzard-1240"
    elif c.amiga_model == "A1200/1260":
        value = "blizzard-1260"
    elif c.amiga_model == "A1200/PPC":
        value = "blizzard-ppc"
    elif c.amiga_model == "A4000/PPC":
        value = "cyberstorm-ppc"
    elif c.amiga_model == "A4000/OS4":
        value = "cyberstorm-ppc"
    else:
        value = "0"
    if f.matches(value, "blizzard-1230-iv"):
        value = "blizzard-1230-iv"
    # elif f.matches(value, "blizzard-1230-iv-scsi"):
    #     value = "blizzard-1230-iv-scsi"
    # elif f.matches(value, "blizzard-1230-iv+scsi"):
    #     value = "blizzard-1230-iv-scsi"
    elif f.matches(value, "blizzard-1240"):
        value = "blizzard-1240"
    elif f.matches(value, "blizzard-1260"):
        value = "blizzard-1260"
    # elif f.matches(value, "blizzard-1260-scsi"):
    #     value = "blizzard-1260-scsi"
    # elif f.matches(value, "blizzard-2060"):
    #     value = "blizzard-2060"
    elif f.matches(value, "blizzard-ppc"):
        value = "blizzard-ppc"
    # elif f.matches(value, "cyberstorm-mk-i"):
    #     value = "cyberstorm-mk-i"
    # elif f.matches(value, "cyberstorm-mk-ii"):
    #     value = "cyberstorm-mk-ii"
    # elif f.matches(value, "cyberstorm-mk-iii"):
    #     value = "cyberstorm-mk-iii"
    elif f.matches(value, "cyberstorm-ppc"):
        value = "cyberstorm-ppc"
    # elif f.matches(value, "dkb-1230"):
    #     value = "dkb-1230"
    # elif f.matches(value, "dkb-1240"):
    #     value = "dkb-1240"
    # elif f.matches(value, "fusion-forty"):
    #     value = "fusion-forty"
    # elif f.matches(value, "warp-engine-a4000"):
    #     value = "warp-engine-a4000"
    c.accelerator = value


# noinspection PyUnusedLocal,SpellCheckingInspection,PyUnresolvedReferences
def _accelerator_memory(c, f):
    if c.accelerator_memory.explicit:
        value = c.accelerator_memory.explicit
    elif c.accelerator == "":
        value = "0"
    elif f.matches(c.accelerator, "blizzard-1230-iv"):
        value = str(32 * 1024)
    elif f.matches(c.accelerator, "blizzard-1240"):
        value = str(32 * 1024)
    elif f.matches(c.accelerator, "blizzard-1260"):
        value = str(32 * 1024)
    elif f.matches(c.accelerator, "blizzard-ppc"):
        value = str(256 * 1024)
    elif f.matches(c.accelerator, "cyberstorm-ppc"):
        value = str(128 * 1024)
    elif f.matches(c.accelerator, "0"):
        value = str(0 * 1024)
    else:
        f.warning("accelerator_memory")
        value = "0"
    c.accelerator_memory = value


# noinspection PyUnusedLocal,SpellCheckingInspection,PyUnresolvedReferences
def _amiga_model(c, f):
    if c.amiga_model.explicit:
        c.amiga_model = c.amiga_model.explicit
    else:
        c.amiga_model = "A500"


# noinspection PyUnusedLocal,SpellCheckingInspection,PyUnresolvedReferences
def _bsdsocket_library(c, f):
    if c.bsdsocket_library.explicit:
        value = c.bsdsocket_library.explicit
    else:
        value = "0"
    c.bsdsocket_library = value


# noinspection PyUnusedLocal,SpellCheckingInspection,PyUnresolvedReferences
def _cdrom_drive_0(c, f):
    pass


# noinspection PyUnusedLocal,SpellCheckingInspection,PyUnresolvedReferences
def _cdrom_drive_count(c, f):
    if c.cdrom_drive_count.explicit:
        value = c.cdrom_drive_count.explicit
    elif c.cdrom_drive_0:
        value = "1"
    elif c.cdrom_image_0:
        value = "1"
    elif c.int_model == "CD32":
        value = "1"
    elif c.int_model == "CDTV":
        value = "1"
    else:
        value = "0"
    c.cdrom_drive_count = value


# noinspection PyUnusedLocal,SpellCheckingInspection,PyUnresolvedReferences
def _cdrom_image_0(c, f):
    pass


# noinspection PyUnusedLocal,SpellCheckingInspection,PyUnresolvedReferences
def _chip_memory(c, f):
    if c.chip_memory.explicit:
        value = c.chip_memory.explicit
    elif c.amiga_model == "A500":
        value = "512"
    elif c.amiga_model == "A500/512K":
        value = "512"
    elif c.amiga_model == "A500+":
        value = "1024"
    elif c.amiga_model == "A600":
        value = "1024"
    elif c.amiga_model == "A1000":
        value = "512"
    elif c.amiga_model == "A1200":
        value = "2048"
    elif c.amiga_model == "A1200/3.0":
        value = "2048"
    elif c.amiga_model == "A1200/020":
        value = "2048"
    elif c.amiga_model == "A1200/1230":
        value = "2048"
    elif c.amiga_model == "A1200/1240":
        value = "2048"
    elif c.amiga_model == "A1200/1260":
        value = "2048"
    elif c.amiga_model == "A1200/PPC":
        value = "2048"
    elif c.amiga_model == "A3000":
        # FIXME: did it usually have 1 MB?
        value = "2048"
    elif c.amiga_model == "A4000":
        value = "2048"
    elif c.amiga_model == "A4000/040":
        value = "2048"
    elif c.amiga_model == "A4000/OS4":
        value = "2048"
    elif c.amiga_model == "A4000/PPC":
        value = "2048"
    elif c.amiga_model == "CD32":
        value = "2048"
    elif c.amiga_model == "CD32/FMV":
        value = "2048"
    elif c.amiga_model == "CDTV":
        value = "512"
    else:
        f.fail("Unknown amiga_model")
        raise Exception("Failed")
    c.chip_memory = value


# noinspection PyUnusedLocal,SpellCheckingInspection,PyUnresolvedReferences
def _cpu(c, f):
    if c.cpu.explicit:
        c.cpu = c.cpu.explicit
    elif c.accelerator == "blizzard-1230-iv":
        c.cpu = "68EC030"
    elif c.accelerator == "blizzard-1240":
        c.cpu = "68040-NOMMU"
    elif c.accelerator == "blizzard-1260":
        c.cpu = "68060-NOMMU"
    elif c.accelerator == "blizzard-ppc":
        c.cpu = "68060-NOMMU"
    elif c.accelerator == "cyberstorm-ppc":
        c.cpu = "68060-NOMMU"
    elif c.amiga_model == "A500":
        c.cpu = "68000"
    elif c.amiga_model == "A500/512K":
        c.cpu = "68000"
    elif c.amiga_model == "A500+":
        c.cpu = "68000"
    elif c.amiga_model == "A600":
        c.cpu = "68000"
    elif c.amiga_model == "A1000":
        c.cpu = "68000"
    elif c.amiga_model == "A1200":
        c.cpu = "68EC020"
    elif c.amiga_model == "A1200/3.0":
        c.cpu = "68EC020"
    elif c.amiga_model == "A1200/020":
        c.cpu = "68020"
    elif c.amiga_model == "A1200/1230":
        c.cpu = "68030"
    elif c.amiga_model == "A1200/1240":
        c.cpu = "68040-NOMMU"
    elif c.amiga_model == "A1200/1260":
        c.cpu = "68060-NOMMU"
    elif c.amiga_model == "A1200/PPC":
        c.cpu = "68060-NOMMU"
    elif c.amiga_model == "A3000":
        c.cpu = "68030"
    elif c.amiga_model == "A4000":
        c.cpu = "68EC030"
    elif c.amiga_model == "A4000/040":
        c.cpu = "68040-NOMMU"
    elif c.amiga_model == "A4000/OS4":
        c.cpu = "68060-NOMMU"
    elif c.amiga_model == "A4000/PPC":
        c.cpu = "68060-NOMMU"
    elif c.amiga_model == "CD32":
        c.cpu = "68EC020"
    elif c.amiga_model == "CD32/FMV":
        c.cpu = "68EC020"
    elif c.amiga_model == "CDTV":
        c.cpu = "68000"
    else:
        f.fail("Unknown amiga_model")
        raise Exception("Failed")


# noinspection PyUnusedLocal,SpellCheckingInspection,PyUnresolvedReferences
def _dongle_type(c, f):
    # FIXME: uae_dongle_type
    if c.dongle_type.explicit:
        c.dongle_type = c.dongle_type.explicit
    else:
        c.dongle_type = "0"


# noinspection PyUnusedLocal,SpellCheckingInspection,PyUnresolvedReferences
def _fast_memory(c, f):
    if c.fast_memory.explicit:
        value = c.fast_memory.explicit
    else:
        value = "0"
    c.fast_memory = value


# noinspection PyUnusedLocal,SpellCheckingInspection,PyUnresolvedReferences
def _floppy_drive_0(c, f):
    pass


# noinspection PyUnusedLocal,SpellCheckingInspection,PyUnresolvedReferences
def _floppy_drive_1(c, f):
    pass


# noinspection PyUnusedLocal,SpellCheckingInspection,PyUnresolvedReferences
def _floppy_drive_2(c, f):
    pass


# noinspection PyUnusedLocal,SpellCheckingInspection,PyUnresolvedReferences
def _floppy_drive_3(c, f):
    pass


# noinspection PyUnusedLocal,SpellCheckingInspection,PyUnresolvedReferences
def _floppy_drive_count(c, f):
    if c.floppy_drive_count.explicit:
        value = c.floppy_drive_count.explicit
    elif c.floppy_drive_3:
        value = "4"
    elif c.floppy_drive_2:
        value = "3"
    elif c.floppy_drive_1:
        value = "2"
    elif c.int_model == "A4000":
        value = "2"
    elif c.floppy_drive_0:
        value = "1"
    elif c.int_model == "CD32":
        value = "0"
    elif c.int_model == "CDTV":
        value = "0"
    elif c.platform == "amiga":
        value = "1"
    elif c.platform == "cd32":
        value = "1"
    elif c.platform == "cdtv":
        value = "1"
    elif c.platform == "":
        value = "1"
    else:
        value = "0"
    c.floppy_drive_count = value


# noinspection PyUnusedLocal,SpellCheckingInspection,PyUnresolvedReferences
def _floppy_drive_speed(c, f):
    if c.floppy_drive_speed.explicit:
        c.floppy_drive_speed = c.floppy_drive_speed.explicit
    else:
        c.floppy_drive_speed = "100"


# noinspection PyUnusedLocal,SpellCheckingInspection,PyUnresolvedReferences
def _fpu(c, f):
    if c.fpu.explicit:
        value = c.fpu.explicit
    elif c.amiga_model == "A3000" and not c.cpu.explicit:
        value = "68882"
    elif c.amiga_model == "A4000" and not c.cpu.explicit:
        value = "68882"
    elif c.cpu == "68000":
        value = "0"
    elif c.cpu == "68010":
        value = "0"
    elif c.cpu == "68EC020":
        value = "0"
    elif c.cpu == "68020":
        value = "0"
    elif c.cpu == "68EC030":
        value = "0"
    elif c.cpu == "68030":
        value = "0"
    elif c.cpu == "68EC040":
        value = "0"
    elif c.cpu == "68LC040":
        value = "0"
    elif c.cpu == "68040-NOMMU":
        value = "68040"
    elif c.cpu == "68040":
        value = "68040"
    elif c.cpu == "68EC060":
        value = "0"
    elif c.cpu == "68LC060":
        value = "0"
    elif c.cpu == "68060-NOMMU":
        value = "68060"
    elif c.cpu == "68060":
        value = "68060"
    else:
        f.fail("Unknown CPU")
        raise Exception("Failed")
    c.fpu = value


# noinspection PyUnusedLocal,SpellCheckingInspection,PyUnresolvedReferences
def _freezer_cartridge(c, f):
    if c.freezer_cartridge.explicit:
        c.freezer_cartridge = c.freezer_cartridge.explicit
        # FIXME: Check valid values
    else:
        c.freezer_cartridge = "0"


# noinspection PyUnusedLocal,SpellCheckingInspection,PyUnresolvedReferences
def _graphics_card(c, f):
    if c.graphics_card.explicit:
        # FIXME: check supported
        value = c.graphics_card.explicit
    else:
        value = ""
    c.graphics_card = value


# noinspection PyUnusedLocal,SpellCheckingInspection,PyUnresolvedReferences
def _graphics_memory(c, f):
    if c.graphics_memory.explicit:
        value = c.graphics_memory.explicit
    elif c.uae_gfxcard_size == "0":
        value = "0"
    else:
        value = int(c.uae_gfxcard_size) * 1024
    c.graphics_memory = value


# noinspection PyUnusedLocal,SpellCheckingInspection,PyUnresolvedReferences
def _int_accelerator_name(c, f):
    # noinspection PyUnresolvedReferences
    if c.int_accelerator_name.explicit:
        f.fail("int_accelerator_name was set explicitly")
    if f.matches(c.uae_cpuboard_type, "none"):
        value = ""
    elif f.matches(c.uae_cpuboard_type, "Blizzard1230IV"):
        value = "Blizzard 1230 IV"
    elif f.matches(c.uae_cpuboard_type, "Blizzard1260"):
        value = "Blizzard 1240/1260"
    elif f.matches(c.uae_cpuboard_type, "Blizzard2060"):
        value = "Blizzard 2060"
    elif f.matches(c.uae_cpuboard_type, "BlizzardPPC"):
        value = "Blizzard PPC"
    elif f.matches(c.uae_cpuboard_type, "CyberStormMK1"):
        value = "CyberStorm MK I"
    elif f.matches(c.uae_cpuboard_type, "CyberStormMK2"):
        value = "CyberStorm MK II"
    elif f.matches(c.uae_cpuboard_type, "CyberStormMK3"):
        value = "CyberStorm MK III"
    elif f.matches(c.uae_cpuboard_type, "CyberStormPPC"):
        value = "Cyberstorm PPC"
    elif f.matches(c.uae_cpuboard_type, "WarpEngineA4000"):
        value = "Warp Engine"
    elif f.matches(c.uae_cpuboard_type, "TekMagic"):
        value = "Tek Magic"
    else:
        value = "Unknown Accelerator (?)"
        f.warning("Unknown accelerator")
    c.int_accelerator_name = value


# noinspection PyUnusedLocal,SpellCheckingInspection,PyUnresolvedReferences
def _int_bogomem_size(c, f):
    # noinspection PyUnresolvedReferences
    if c.int_bogomem_size.explicit:
        f.fail("int_bogomem_size was set explicitly")
    if c.slow_memory:
        value = str(int(c.slow_memory) * 1024)
    else:
        value = "0"
    if value == "0":
        pass
    elif value == "524288":
        pass
    elif value == "1048576":
        pass
    elif value == "1572864":
        pass
    elif value == "1835008":
        pass
    else:
        f.warning("Unsupported slow memory size: " + value)
    c.int_bogomem_size = value


# noinspection PyUnusedLocal,SpellCheckingInspection,PyUnresolvedReferences
def _int_chipmem_size(c, f):
    # noinspection PyUnresolvedReferences
    if c.int_chipmem_size.explicit:
        f.fail("int_chipmem_size was set explicitly")
    if c.chip_memory:
        value = str(int(c.chip_memory) * 1024)
    else:
        value = "0"
    if value == "0":
        pass
    elif value == "262144":
        pass
    elif value == "524288":
        pass
    elif value == "1048576":
        pass
    elif value == "1572864":
        pass
    elif value == "2097152":
        pass
    elif value == "4194304":
        pass
    elif value == "8388608":
        pass
    else:
        f.warning("Unsupported chip memory size: " + value)
    c.int_chipmem_size = value


# noinspection PyUnusedLocal,SpellCheckingInspection,PyUnresolvedReferences
def _int_chipset_name(c, f):
    # noinspection PyUnresolvedReferences
    if c.int_chipset_name.explicit:
        f.fail("int_chipset_name was set explicitly")
    t = f.lower(c.uae_chipset)
    if t == "ocs":
        value = "OCS"
    elif t == "ecs":
        value = "ECS"
    elif t == "ecs_agnus":
        value = "ECS Agnus"
    elif t == "ecs_denise":
        value = "ECS Denise"
    elif t == "aga":
        value = "AGA"
    else:
        value = "Unknown"
        f.warning("Unknown chipset")
    c.int_chipset_name = value


# noinspection PyUnusedLocal,SpellCheckingInspection,PyUnresolvedReferences
def _int_cpu_name(c, f):
    # noinspection PyUnresolvedReferences
    if c.int_cpu_name.explicit:
        f.fail("int_cpu_name was set explicitly")
    if f.matches(c.uae_cpu_model, "68000"):
        value = "68000"
    elif f.matches(c.uae_cpu_model, "68010"):
        value = "68010"
    elif f.matches(c.uae_cpu_model, "68020"):
        if f.matches(c.uae_cpu_24bit_addressing, "true"):
            value = "68EC020"
        else:
            value = "68020"
    elif f.matches(c.uae_cpu_model, "68030"):
        if f.matches(c.uae_mmu_model, "68030"):
            value = "68030"
        else:
            value = "68EC030"
    elif f.matches(c.uae_cpu_model, "68040"):
        if f.matches(c.uae_fpu_model, "68040"):
            value = "68040"
        elif f.matches(c.uae_mmu_model, "68040"):
            value = "68LC040"
        else:
            value = "68EC040"
    elif f.matches(c.uae_cpu_model, "68060"):
        if f.matches(c.uae_fpu_model, "68060"):
            value = "68060"
        elif f.matches(c.uae_mmu_model, "68060"):
            value = "68LC060"
        else:
            value = "68EC060"
    else:
        f.fail("Unknown CPU")
        raise Exception("Failed")
    c.int_cpu_name = value


# noinspection PyUnusedLocal,SpellCheckingInspection,PyUnresolvedReferences
def _int_cpuboardmem1_size(c, f):
    # noinspection PyUnresolvedReferences
    if c.int_cpuboardmem1_size.explicit:
        f.fail("int_cpuboardmem1_size was set explicitly")
    if c.accelerator_memory:
        value = str(int(c.accelerator_memory) * 1024)
    else:
        value = "0"
    c.int_cpuboardmem1_size = value


# noinspection PyUnusedLocal,SpellCheckingInspection,PyUnresolvedReferences
def _int_default_floppy_type(c, f):
    # noinspection PyUnresolvedReferences
    if c.int_default_floppy_type.explicit:
        f.fail("int_default_floppy_type was set explicitly")
    if c.int_model == "A3000":
        value = "1"
    elif c.int_model == "A4000":
        value = "1"
    else:
        value = "0"
    c.int_default_floppy_type = value


# noinspection PyUnusedLocal,SpellCheckingInspection,PyUnresolvedReferences
def _int_fastmem_size(c, f):
    # noinspection PyUnresolvedReferences
    if c.int_fastmem_size.explicit:
        f.fail("int_fastmem_size was set explicitly")
    if c.fast_memory:
        value = str(int(c.fast_memory) * 1024)
    else:
        value = "0"
    if value == "0":
        pass
    elif value == "65536":
        pass
    elif value == "131072":
        pass
    elif value == "262144":
        pass
    elif value == "524288":
        pass
    elif value == "1048576":
        pass
    elif value == "2097152":
        pass
    elif value == "4194304":
        pass
    elif value == "8388608":
        pass
    else:
        f.warning("Unsupported Zorro II fast memory size: " + value)
    c.int_fastmem_size = value


# noinspection PyUnusedLocal,SpellCheckingInspection,PyUnresolvedReferences
def _int_graphics_card_bus(c, f):
    # noinspection PyUnresolvedReferences
    if c.int_graphics_card_bus.explicit:
        f.fail("int_graphics_card_bus was set explicitly")
    t = c.uae_gfxcard_type
    if t == "":
        value = ""
    elif t == "PicassoII":
        value = "zorro-ii"
    elif t == "PicassoII+":
        value = "zorro-ii"
    elif t == "PicassoIV_Z2":
        value = "zorro-ii"
    elif t == "PicassoIV_Z3":
        value = "zorro-iii"
    elif t == "ZorroII":
        value = "zorro-ii"
    elif t == "ZorroIII":
        value = "zorro-iii"
    else:
        f.warning("Unrecognized graphics card: " + t)
        value = ""
    if value == "zorro-iii" and c.uae_cpu_24bit_addressing == "true":
        f.warning("Zorro III graphics card cannot be used with 24-bit CPU")
    c.int_graphics_card_bus = value


# noinspection PyUnusedLocal,SpellCheckingInspection,PyUnresolvedReferences
def _int_graphics_card_name(c, f):
    # noinspection PyUnresolvedReferences
    if c.int_graphics_card_name.explicit:
        f.fail("int_graphics_card_name was set explicitly")
    t = c.uae_gfxcard_type
    if t == "PicassoII":
        value = "Picasso II"
    elif t == "PicassoII+":
        value = "Picasso II+"
    elif t == "PicassoIV_Z2":
        value = "Picasso IV"
    elif t == "PicassoIV_Z3":
        value = "Picasso IV"
    elif t == "ZorroII":
        value = "UAEGFX"
    elif t == "ZorroIII":
        value = "UAEGFX"
    else:
        value = "Unknown GFX Card"
    c.int_graphics_card_name = value


# noinspection PyUnusedLocal,SpellCheckingInspection,PyUnresolvedReferences
def _int_kickstart_ext_sha1(c, f):
    # noinspection PyUnresolvedReferences
    if c.int_kickstart_ext_sha1.explicit:
        f.fail("int_kickstart_ext_sha1 was set explicitly")
    t = c.amiga_model
    if t == "A500":
        value = ""
    elif t == "A500/512K":
        value = ""
    elif t == "A500+":
        value = ""
    elif t == "A600":
        value = ""
    elif t == "A1000":
        value = ""
    elif t == "A1200":
        value = ""
    elif t == "A1200/3.0":
        value = ""
    elif t == "A1200/020":
        value = ""
    elif t == "A1200/1230":
        value = ""
    elif t == "A1200/1240":
        value = ""
    elif t == "A1200/1260":
        value = ""
    elif t == "A1200/PPC":
        value = ""
    elif t == "A3000":
        value = ""
    elif t == "A4000":
        value = ""
    elif t == "A4000/040":
        value = ""
    elif t == "A4000/OS4":
        value = ""
    elif t == "A4000/PPC":
        value = ""
    elif t == "CD32":
        value = "5bef3d628ce59cc02a66e6e4ae0da48f60e78f7f"
    elif t == "CD32/FMV":
        value = "5bef3d628ce59cc02a66e6e4ae0da48f60e78f7f"
    elif t == "CDTV":
        value = "7ba40ffa17e500ed9fed041f3424bd81d9c907be"
    else:
        f.fail("Unknown amiga_model: " + t)
        raise Exception("Failed")
    c.int_kickstart_ext_sha1 = value


# noinspection PyUnusedLocal,SpellCheckingInspection,PyUnresolvedReferences
def _int_kickstart_revision(c, f):
    # noinspection PyUnresolvedReferences
    if c.int_kickstart_revision.explicit:
        f.fail("int_kickstart_revision was set explicitly")
    t = c.int_kickstart_sha1
    if t == "02843c4253bbd29aba535b0aa3bd9a85034ecde4":
        # Kickstart v2.05 rev 37.350 (1992)(Commodore)(A600HD)[!]
        value = "37.350"
    elif t == "11f9e62cf299f72184835b7b2a70a16333fc0d88":
        # Kickstart v1.2 rev 33.180 (1986)(Commodore)(A500-A2000)[!]
        value = "33.180"
    elif t == "3525be8887f79b5929e017b42380a79edfee542d":
        # Kickstart v3.1 rev 40.60 (1993)(Commodore)(CD32)
        value = "40.60"
    elif t == "5fe04842d04a489720f0f4bb0e46948199406f49":
        # Kickstart v3.1 rev 40.68 (1993)(Commodore)(A4000)
        value = "40.68"
    elif t == "70033828182fffc7ed106e5373a8b89dda76faa5":
        # Kickstart v3.0 rev 39.106 (1992)(Commodore)(A1200)[!]
        value = "39.106"
    elif t == "891e9a547772fe0c6c19b610baf8bc4ea7fcb785":
        # Kickstart v1.3 rev 34.5 (1987)(Commodore)(A500-A1000-A2000-CDTV)[!]
        value = "34.5"
    elif t == "c5839f5cb98a7a8947065c3ed2f14f5f42e334a1":
        # Kickstart v2.04 rev 37.175 (1991)(Commodore)(A500+)[!]
        value = "37.175"
    elif t == "e21545723fe8374e91342617604f1b3d703094f1":
        # Kickstart v3.1 rev 40.68 (1993)(Commodore)(A1200)[!]
        value = "40.68"
    elif t == "f8e210d72b4c4853e0c9b85d223ba20e3d1b36ee":
        # Kickstart v3.1 r40.68 (1993)(Commodore)(A3000).rom
        value = "40.68"
    else:
        value = "???"
    c.int_kickstart_revision = value


# noinspection PyUnusedLocal,SpellCheckingInspection,PyUnresolvedReferences
def _int_kickstart_sha1(c, f):
    # noinspection PyUnresolvedReferences
    if c.int_kickstart_sha1.explicit:
        f.fail("int_kickstart_sha1 was set explicitly")
    if c.amiga_model == "A500":
        value = "891e9a547772fe0c6c19b610baf8bc4ea7fcb785"
    elif c.amiga_model == "A500/512K":
        value = "891e9a547772fe0c6c19b610baf8bc4ea7fcb785"
    elif c.amiga_model == "A500+":
        value = "c5839f5cb98a7a8947065c3ed2f14f5f42e334a1"
    elif c.amiga_model == "A600":
        value = "02843c4253bbd29aba535b0aa3bd9a85034ecde4"
    elif c.amiga_model == "A1000":
        value = "11f9e62cf299f72184835b7b2a70a16333fc0d88"
    elif c.amiga_model == "A1200":
        value = "e21545723fe8374e91342617604f1b3d703094f1"
    elif c.amiga_model == "A1200/3.0":
        value = "70033828182fffc7ed106e5373a8b89dda76faa5"
    elif c.amiga_model == "A1200/020":
        value = "e21545723fe8374e91342617604f1b3d703094f1"
    elif c.amiga_model == "A1200/1230":
        value = "e21545723fe8374e91342617604f1b3d703094f1"
    elif c.amiga_model == "A1200/1240":
        value = "e21545723fe8374e91342617604f1b3d703094f1"
    elif c.amiga_model == "A1200/1260":
        value = "e21545723fe8374e91342617604f1b3d703094f1"
    elif c.amiga_model == "A1200/PPC":
        value = "e21545723fe8374e91342617604f1b3d703094f1"
    elif c.amiga_model == "A3000":
        value = "f8e210d72b4c4853e0c9b85d223ba20e3d1b36ee"
    elif c.amiga_model == "A4000":
        value = "5fe04842d04a489720f0f4bb0e46948199406f49"
    elif c.amiga_model == "A4000/040":
        value = "5fe04842d04a489720f0f4bb0e46948199406f49"
    elif c.amiga_model == "A4000/OS4":
        value = "5fe04842d04a489720f0f4bb0e46948199406f49"
    elif c.amiga_model == "A4000/PPC":
        value = "5fe04842d04a489720f0f4bb0e46948199406f49"
    elif c.amiga_model == "CD32":
        value = "3525be8887f79b5929e017b42380a79edfee542d"
    elif c.amiga_model == "CD32/FMV":
        value = "3525be8887f79b5929e017b42380a79edfee542d"
    elif c.amiga_model == "CDTV":
        value = "891e9a547772fe0c6c19b610baf8bc4ea7fcb785"
    else:
        f.fail("Unknown amiga_model")
        raise Exception("Failed")
    c.int_kickstart_sha1 = value


# noinspection PyUnusedLocal,SpellCheckingInspection,PyUnresolvedReferences
def _int_kickstart_version(c, f):
    # noinspection PyUnresolvedReferences
    if c.int_kickstart_version.explicit:
        f.fail("int_kickstart_version was set explicitly")
    t = c.int_kickstart_revision
    if t == "33.180":
        value = "1.2"
    elif t == "34.5":
        value = "1.3"
    elif t == "37.175":
        value = "2.04"
    elif t == "37.350":
        value = "2.05"
    elif t == "39.106":
        value = "3.0"
    elif t == "40.60":
        value = "3.1"
    elif t == "40.68":
        value = "3.1"
    else:
        value = "???"
    c.int_kickstart_version = value


# noinspection PyUnusedLocal,SpellCheckingInspection,PyUnresolvedReferences
def _int_mbresmem_low_size(c, f):
    # noinspection PyUnresolvedReferences
    if c.int_mbresmem_low_size.explicit:
        f.fail("int_mbresmem_low_size was set explicitly")
    if int(c.uae_a3000mem_size):
        value = str(int(c.uae_a3000mem_size) * 1024 * 1024)
    else:
        value = "0"
    c.int_mbresmem_low_size = value


# noinspection PyUnusedLocal,SpellCheckingInspection,PyUnresolvedReferences
def _int_model(c, f):
    # noinspection PyUnresolvedReferences
    if c.int_model.explicit:
        f.fail("int_model was set explicitly")
    if c.amiga_model == "A500":
        c.int_model = "A500"
    elif c.amiga_model == "A500/512K":
        c.int_model = "A500"
    elif c.amiga_model == "A500+":
        c.int_model = "A500+"
    elif c.amiga_model == "A600":
        c.int_model = "A600"
    elif c.amiga_model == "A1000":
        c.int_model = "A1000"
    elif c.amiga_model == "A1200":
        c.int_model = "A1200"
    elif c.amiga_model == "A1200/3.0":
        c.int_model = "A1200"
    elif c.amiga_model == "A1200/020":
        c.int_model = "A1200"
    elif c.amiga_model == "A1200/1230":
        c.int_model = "A1200"
    elif c.amiga_model == "A1200/1240":
        c.int_model = "A1200"
    elif c.amiga_model == "A1200/1260":
        c.int_model = "A1200"
    elif c.amiga_model == "A1200/PPC":
        c.int_model = "A1200"
    elif c.amiga_model == "A3000":
        c.int_model = "A3000"
    elif c.amiga_model == "A4000":
        c.int_model = "A4000"
    elif c.amiga_model == "A4000/040":
        c.int_model = "A4000"
    elif c.amiga_model == "A4000/OS4":
        c.int_model = "A4000"
    elif c.amiga_model == "A4000/PPC":
        c.int_model = "A4000"
    elif c.amiga_model == "CD32":
        c.int_model = "CD32"
    elif c.amiga_model == "CD32/FMV":
        c.int_model = "CD32"
    elif c.amiga_model == "CDTV":
        c.int_model = "CDTV"
    else:
        f.fail("Unknown amiga_model")
        raise Exception("Failed")


# noinspection PyUnusedLocal,SpellCheckingInspection,PyUnresolvedReferences
def _int_model_name(c, f):
    # noinspection PyUnresolvedReferences
    if c.int_model_name.explicit:
        f.fail("int_model_name was set explicitly")
    if c.int_model == "A500":
        value = "Amiga 500"
    elif c.int_model == "A500+":
        value = "Amiga 500+"
    elif c.int_model == "A600":
        value = "Amiga 600"
    elif c.int_model == "A1000":
        value = "Amiga 1000"
    elif c.int_model == "A1200":
        value = "Amiga 1200"
    elif c.int_model == "A3000":
        value = "Amiga 3000"
    elif c.int_model == "A4000":
        value = "Amiga 4000"
    elif c.int_model == "CD32":
        value = "Amiga CD32"
    elif c.int_model == "CDTV":
        value = "Commodore CDTV"
    else:
        f.fail("Unknown amiga_model")
        raise Exception("Failed")
    c.int_model_name = value


# noinspection PyUnusedLocal,SpellCheckingInspection,PyUnresolvedReferences
def _int_ppc_model(c, f):
    # noinspection PyUnresolvedReferences
    if c.int_ppc_model.explicit:
        f.fail("int_ppc_model was set explicitly")
    if f.matches(c.uae_cpuboard_type, "BlizzardPPC"):
        value = "603ev"
    elif f.matches(c.uae_cpuboard_type, "CyberStormPPC"):
        value = "604e"
    else:
        value = ""
    c.int_ppc_model = value


# noinspection PyUnusedLocal,SpellCheckingInspection,PyUnresolvedReferences
def _int_uae_boot_rom(c, f):
    # noinspection PyUnresolvedReferences
    if c.int_uae_boot_rom.explicit:
        f.fail("int_uae_boot_rom was set explicitly")
    if c.uae_bsdsocket_emu == "true":
        value = "true"
    elif c.uae_sana2 == "true":
        value = "true"
    elif c.uae_gfxcard_type == "ZorroII" and c.uae_gfxcard_size != "0":
        value = "true"
    elif c.uae_gfxcard_type == "ZorroIII" and c.uae_gfxcard_size != "0":
        value = "true"
    elif c.uae_z3chipmem_size != "0":
        value = "true"
    else:
        value = "false"
    # FIXME:
    # if (nr_directory_units (NULL))
    #     return b;
    # if (nr_directory_units (&currprefs))
    #     return b;
    # if (currprefs.uaeserial)
    #     return b;
    # if (currprefs.scsi == 1)
    #     return b;
    # if (currprefs.input_tablet > 0)
    # 	return b;
    # if (currprefs.rtgmem_size && currprefs.rtgmem_type < GFXBOARD_HARDWARE)
    #     return b;
    # if (currprefs.win32_automount_removable)
    #     return b;
    # if (currprefs.chipmem_size > 2 * 1024 * 1024)
    #     return b;
    c.int_uae_boot_rom = value


# noinspection PyUnusedLocal,SpellCheckingInspection,PyUnresolvedReferences
def _int_z3chipmem_size(c, f):
    # noinspection PyUnresolvedReferences
    if c.int_z3chipmem_size.explicit:
        f.fail("int_z3chipmem_size was set explicitly")
    if int(c.uae_z3chipmem_size):
        value = str(int(c.uae_z3chipmem_size) * 1024 * 1024)
    else:
        value = "0"
    c.int_z3chipmem_size = value


# noinspection PyUnusedLocal,SpellCheckingInspection,PyUnresolvedReferences
def _int_z3fastmem_size(c, f):
    # noinspection PyUnresolvedReferences
    if c.int_z3fastmem_size.explicit:
        f.fail("int_z3fastmem_size was set explicitly")
    if int(c.uae_z3mem_size):
        value = str(int(c.uae_z3mem_size) * 1024 * 1024)
    # if c.zorro_iii_memory:
    #     value = str(int(c.zorro_iii_memory) * 1024)
    else:
        value = "0"
    c.int_z3fastmem_size = value


# noinspection PyUnusedLocal,SpellCheckingInspection,PyUnresolvedReferences
def _jit_compiler(c, f):
    if c.jit_compiler.explicit:
        c.jit_compiler = c.jit_compiler.explicit
    else:
        c.jit_compiler = "0"


# noinspection PyUnusedLocal,SpellCheckingInspection,PyUnresolvedReferences
def _joystick_port_0_mode(c, f):
    if c.joystick_port_0_mode.explicit:
        value = c.joystick_port_0_mode.explicit
    elif c.amiga_model == "CD32":
        value = "cd32 gamepad"
    else:
        # FIXME: depends on actual device in joystick_port_0...
        value = "mouse"
    c.joystick_port_0_mode = value


# noinspection PyUnusedLocal,SpellCheckingInspection,PyUnresolvedReferences
def _joystick_port_1_mode(c, f):
    if c.joystick_port_1_mode.explicit:
        value = c.joystick_port_1_mode.explicit
    elif c.amiga_model == "CD32":
        value = "cd32 gamepad"
    else:
        # FIXME: depends on actual device in joystick_port_1...
        value = "joystick"
    c.joystick_port_1_mode = value


# noinspection PyUnusedLocal,SpellCheckingInspection,PyUnresolvedReferences
def _joystick_port_2_mode(c, f):
    if c.joystick_port_2_mode.explicit:
        value = c.joystick_port_2_mode.explicit
    else:
        # FIXME: depends on actual device in joystick_port_2...?
        value = "nothing"
    c.joystick_port_2_mode = value


# noinspection PyUnusedLocal,SpellCheckingInspection,PyUnresolvedReferences
def _joystick_port_3_mode(c, f):
    if c.joystick_port_3_mode.explicit:
        value = c.joystick_port_3_mode.explicit
    else:
        # FIXME: depends on actual device in joystick_port_3...?
        value = "nothing"
    c.joystick_port_3_mode = value


# noinspection PyUnusedLocal,SpellCheckingInspection,PyUnresolvedReferences
def _kickstart_ext_file(c, f):
    if c.kickstart_file.explicit:
        value = c.kickstart_file.explicit
    else:
        value = ""
    c.kickstart_ext_file = value


# noinspection PyUnusedLocal,SpellCheckingInspection,PyUnresolvedReferences
def _kickstart_file(c, f):
    if c.kickstart_file.explicit:
        value = c.kickstart_file.explicit
    else:
        value = ""
    c.kickstart_file = value


# noinspection PyUnusedLocal,SpellCheckingInspection,PyUnresolvedReferences
def _motherboard_ram(c, f):
    if c.motherboard_ram.explicit:
        value = c.motherboard_ram.explicit
    elif c.int_model == "A3000":
        value = "8192"
    elif c.int_model == "A4000":
        # FIXME: should PPC / OS4 models be excluded?
        value = "8192"
    else:
        value = "0"
    c.motherboard_ram = value


# noinspection PyUnusedLocal,SpellCheckingInspection,PyUnresolvedReferences
def _network_card(c, f):
    if c.network_card.explicit:
        # FIXME: check supported
        value = c.network_card.explicit
        if f.matches(value, "a2065"):
            value = "a2065"
        else:
            f.warning(value + ": invalid value")
            value = "0"
    else:
        value = "0"
    c.network_card = value


# noinspection PyUnusedLocal,SpellCheckingInspection,PyUnresolvedReferences
def _platform(c, f):
    pass


# noinspection PyUnusedLocal,SpellCheckingInspection,PyUnresolvedReferences
def _slow_memory(c, f):
    if c.slow_memory.explicit:
        value = c.slow_memory.explicit
    elif c.amiga_model == "A500":
        value = "512"
    else:
        value = "0"
    c.slow_memory = value


# noinspection PyUnusedLocal,SpellCheckingInspection,PyUnresolvedReferences
def _sound_card(c, f):
    if c.sound_card.explicit:
        # FIXME: check supported
        value = c.sound_card.explicit
        if f.matches(value, "toccata"):
            value = "toccata"
        else:
            f.warning(value + ": invalid value")
            value = "0"
    else:
        value = "0"
    c.sound_card = value


# noinspection PyUnusedLocal,SpellCheckingInspection,PyUnresolvedReferences
def _uae_a2065(c, f):
    if c.uae_a2065.explicit:
        # FIXME: ok? keep already specified value
        value = c.uae_a2065.explicit
        # FIXME: check value
    elif c.network_card == "a2065":
        value = "slirp"
    else:
        value = ""
    c.uae_a2065 = value


# noinspection PyUnusedLocal,SpellCheckingInspection,PyUnresolvedReferences
def _uae_a3000mem_size(c, f):
    if c.uae_a3000mem_size.explicit:
        value = c.uae_a3000mem_size.explicit
    elif c.motherboard_ram != "":
        value = str(int(c.motherboard_ram) // 1024)
    # elif c.int_model == "A3000":
    #     value = "8"
    # elif c.int_model == "A4000":
    #     # FIXME: should PPC / OS4 models be excluded?
    #     value = "8"
    else:
        value = "0"
    c.uae_a3000mem_size = value


# noinspection PyUnusedLocal,SpellCheckingInspection,PyUnresolvedReferences
def _uae_bogomem_size(c, f):
    pass


# noinspection PyUnusedLocal,SpellCheckingInspection,PyUnresolvedReferences
def _uae_bsdsocket_emu(c, f):
    if c.uae_bsdsocket_emu.explicit:
        value = c.uae_bsdsocket_emu.explicit
        # FIXME: normalize to "true" or "false"
    elif c.bsdsocket_library == "1":
        value = "true"
    else:
        value = "false"
    c.uae_bsdsocket_emu = value


# noinspection PyUnusedLocal,SpellCheckingInspection,PyUnresolvedReferences
def _uae_cd32cd(c, f):
    if c.uae_cd32cd.explicit:
        # FIXME: boolean
        value = c.uae_cd32cd.explicit
    elif c.int_model == "CD32":
        value = "true"
    else:
        value = "false"
    c.uae_cd32cd = value


# noinspection PyUnusedLocal,SpellCheckingInspection,PyUnresolvedReferences
def _uae_cd32fmv(c, f):
    if c.uae_cd32fmv.explicit:
        # FIXME: boolean
        value = c.uae_cd32fmv.explicit
    elif c.amiga_model == "CD32/FMV":
        value = "true"
    else:
        value = "false"
    c.uae_cd32fmv = value


# noinspection PyUnusedLocal,SpellCheckingInspection,PyUnresolvedReferences
def _uae_chipmem_size(c, f):
    pass


# noinspection PyUnusedLocal,SpellCheckingInspection,PyUnresolvedReferences
def _uae_chipset(c, f):
    if c.uae_chipset.explicit:
        if int(c.int_chipmem_size) >= 1048576:
            value = "ecs_agnus"
        else:
            value = "ocs"
    elif c.amiga_model == "A500":
        if int(c.int_chipmem_size) >= 1048576:
            value = "ecs_agnus"
        else:
            value = "ocs"
    elif c.amiga_model == "A500/512K":
        value = "ocs"
    elif c.amiga_model == "A500+":
        value = "ecs"
    elif c.amiga_model == "A600":
        value = "ecs"
    elif c.amiga_model == "A1000":
        value = "ocs"
    elif c.amiga_model == "A1200":
        value = "aga"
    elif c.amiga_model == "A1200/3.0":
        value = "aga"
    elif c.amiga_model == "A1200/020":
        value = "aga"
    elif c.amiga_model == "A1200/1230":
        value = "aga"
    elif c.amiga_model == "A1200/1240":
        value = "aga"
    elif c.amiga_model == "A1200/1260":
        value = "aga"
    elif c.amiga_model == "A1200/PPC":
        value = "aga"
    elif c.amiga_model == "A3000":
        value = "ecs"
    elif c.amiga_model == "A4000":
        value = "aga"
    elif c.amiga_model == "A4000/040":
        value = "aga"
    elif c.amiga_model == "A4000/OS4":
        value = "aga"
    elif c.amiga_model == "A4000/PPC":
        value = "aga"
    elif c.amiga_model == "CD32":
        value = "aga"
    elif c.amiga_model == "CD32/FMV":
        value = "aga"
    elif c.amiga_model == "CDTV":
        value = "ecs_agnus"
    else:
        f.fail("Unknown amiga_model")
        raise Exception("Failed")
    c.uae_chipset = value


# noinspection PyUnusedLocal,SpellCheckingInspection,PyUnresolvedReferences
def _uae_chipset_compatible(c, f):
    if c.uae_chipset_compatible.explicit:
        value = c.uae_chipset_compatible.explicit
    elif c.amiga_model == "A500":
        value = "A500"
    elif c.amiga_model == "A500/512K":
        value = "A500"
    elif c.amiga_model == "A500+":
        value = "A500+"
    elif c.amiga_model == "A600":
        value = "A600"
    elif c.amiga_model == "A1000":
        value = "A1000"
    elif c.amiga_model == "A1200":
        value = "A1200"
    elif c.amiga_model == "A1200/3.0":
        value = "A1200"
    elif c.amiga_model == "A1200/020":
        value = "A1200"
    elif c.amiga_model == "A1200/1230":
        value = "A1200"
    elif c.amiga_model == "A1200/1240":
        value = "A1200"
    elif c.amiga_model == "A1200/1260":
        value = "A1200"
    elif c.amiga_model == "A1200/PPC":
        value = "A1200"
    elif c.amiga_model == "A3000":
        value = "A3000"
    elif c.amiga_model == "A4000":
        value = "A4000"
    elif c.amiga_model == "A4000/040":
        value = "A4000"
    elif c.amiga_model == "A4000/OS4":
        value = "A4000"
    elif c.amiga_model == "A4000/PPC":
        value = "A4000"
    elif c.amiga_model == "CD32":
        value = "CD32"
    elif c.amiga_model == "CD32/FMV":
        value = "CD32"
    elif c.amiga_model == "CDTV":
        value = "CDTV"
    else:
        f.fail("Unknown amiga_model")
        raise Exception("Failed")
    c.uae_chipset_compatible = value


# noinspection PyUnusedLocal,SpellCheckingInspection,PyUnresolvedReferences
def _uae_cpu_24bit_addressing(c, f):
    if c.uae_cpu_24bit_addressing.explicit:
        c.uae_cpu_24bit_addressing = c.uae_cpu_24bit_addressing.explicit
    elif c.cpu == "68000":
        c.uae_cpu_24bit_addressing = "true"
    elif c.cpu == "68010":
        c.uae_cpu_24bit_addressing = "true"
    elif c.cpu == "68EC020":
        c.uae_cpu_24bit_addressing = "true"
    elif c.cpu == "68020":
        c.uae_cpu_24bit_addressing = "false"
    elif c.cpu == "68EC030":
        c.uae_cpu_24bit_addressing = "false"
    elif c.cpu == "68030":
        c.uae_cpu_24bit_addressing = "false"
    elif c.cpu == "68EC040":
        c.uae_cpu_24bit_addressing = "false"
    elif c.cpu == "68LC040":
        c.uae_cpu_24bit_addressing = "false"
    elif c.cpu == "68040-NOMMU":
        c.uae_cpu_24bit_addressing = "false"
    elif c.cpu == "68040":
        c.uae_cpu_24bit_addressing = "false"
    elif c.cpu == "68EC060":
        c.uae_cpu_24bit_addressing = "false"
    elif c.cpu == "68LC060":
        c.uae_cpu_24bit_addressing = "false"
    elif c.cpu == "68060-NOMMU":
        c.uae_cpu_24bit_addressing = "false"
    elif c.cpu == "68060":
        c.uae_cpu_24bit_addressing = "false"
    else:
        f.fail("Unknown CPU")
        raise Exception("Failed")


# noinspection PyUnusedLocal,SpellCheckingInspection,PyUnresolvedReferences
def _uae_cpu_model(c, f):
    if c.uae_cpu_model.explicit:
        value = c.uae_cpu_model.explicit
    elif c.cpu == "68000":
        value = "68000"
    elif c.cpu == "68010":
        value = "68010"
    elif c.cpu == "68EC020":
        value = "68020"
    elif c.cpu == "68020":
        value = "68020"
    elif c.cpu == "68EC030":
        value = "68030"
    elif c.cpu == "68030":
        value = "68030"
    elif c.cpu == "68EC040":
        value = "68040"
    elif c.cpu == "68LC040":
        value = "68040"
    elif c.cpu == "68040-NOMMU":
        value = "68040"
    elif c.cpu == "68040":
        value = "68040"
    elif c.cpu == "68EC060":
        value = "68060"
    elif c.cpu == "68LC060":
        value = "68060"
    elif c.cpu == "68060-NOMMU":
        value = "68060"
    elif c.cpu == "68060":
        value = "68060"
    else:
        f.fail("Unknown CPU")
        raise Exception("Failed")
    c.uae_cpu_model = value


# noinspection PyUnusedLocal,SpellCheckingInspection,PyUnresolvedReferences
def _uae_cpuboard_type(c, f):
    if c.uae_cpuboard_type.explicit:
        value = c.uae_cpuboard_type.explicit
    elif f.matches(c.accelerator, "0"):
        value = "none"
    elif f.matches(c.accelerator, "blizzard-1230-iv"):
        value = "Blizzard1230IV"
    elif f.matches(c.accelerator, "blizzard-1240"):
        value = "Blizzard1260"
    elif f.matches(c.accelerator, "blizzard-1260"):
        value = "Blizzard1260"
    elif f.matches(c.accelerator, "blizzard-2060"):
        value = "Blizzard2060"
    elif f.matches(c.accelerator, "blizzard-ppc"):
        value = "BlizzardPPC"
    elif f.matches(c.accelerator, "cyberstorm-mk-i"):
        value = "CyberStormMK1"
    elif f.matches(c.accelerator, "cyberstorm-mk-ii"):
        value = "CyberStormMK2"
    elif f.matches(c.accelerator, "cyberstorm-mk-iii"):
        value = "CyberStormMK3"
    elif f.matches(c.accelerator, "cyberstorm-ppc"):
        value = "CyberStormPPC"
    elif f.matches(c.accelerator, "warp-engine-a4000"):
        value = "WarpEngineA4000"
    elif f.matches(c.accelerator, "tek-magic"):
        value = "TekMagic"
    elif f.matches(c.accelerator, "dkb-1230"):
        value = "DKB12x0"
    elif f.matches(c.accelerator, "dkb-1240"):
        value = "DKB12x0"
    elif f.matches(c.accelerator, "fusion-forty"):
        value = "FusionForty"
    else:
        f.fail("Unknown accelerator")
        raise Exception("Failed")
    c.uae_cpuboard_type = value


# noinspection PyUnusedLocal,SpellCheckingInspection,PyUnresolvedReferences
def _uae_fastmem_size(c, f):
    pass


# noinspection PyUnusedLocal,SpellCheckingInspection,PyUnresolvedReferences
def _uae_floppy0(c, f):
    if c.uae_floppy0.explicit:
        value = c.uae_floppy0.explicit
    else:
        value = c.floppy_drive_0
    c.uae_floppy0 = value


# noinspection PyUnusedLocal,SpellCheckingInspection,PyUnresolvedReferences
def _uae_floppy0type(c, f):
    if c.uae_floppy0type.explicit:
        value = c.uae_floppy0type.explicit
    elif int(c.floppy_drive_count) > 0:
        value = c.int_default_floppy_type
    else:
        value = "-1"
    c.uae_floppy0type = value


# noinspection PyUnusedLocal,SpellCheckingInspection,PyUnresolvedReferences
def _uae_floppy1(c, f):
    if c.uae_floppy1.explicit:
        value = c.uae_floppy1.explicit
    else:
        value = c.floppy_drive_1
    c.uae_floppy1 = value


# noinspection PyUnusedLocal,SpellCheckingInspection,PyUnresolvedReferences
def _uae_floppy1type(c, f):
    if c.uae_floppy1type.explicit:
        value = c.uae_floppy1type.explicit
    elif int(c.floppy_drive_count) > 1:
        value = c.int_default_floppy_type
    else:
        value = "-1"
    c.uae_floppy1type = value


# noinspection PyUnusedLocal,SpellCheckingInspection,PyUnresolvedReferences
def _uae_floppy2(c, f):
    if c.uae_floppy2.explicit:
        value = c.uae_floppy2.explicit
    else:
        value = c.floppy_drive_2
    c.uae_floppy2 = value


# noinspection PyUnusedLocal,SpellCheckingInspection,PyUnresolvedReferences
def _uae_floppy2type(c, f):
    if c.uae_floppy2type.explicit:
        value = c.uae_floppy2type.explicit
    elif int(c.floppy_drive_count) > 2:
        value = c.int_default_floppy_type
    else:
        value = "-1"
    c.uae_floppy2type = value


# noinspection PyUnusedLocal,SpellCheckingInspection,PyUnresolvedReferences
def _uae_floppy3(c, f):
    if c.uae_floppy3.explicit:
        value = c.uae_floppy3.explicit
    else:
        value = c.floppy_drive_3
    c.uae_floppy3 = value


# noinspection PyUnusedLocal,SpellCheckingInspection,PyUnresolvedReferences
def _uae_floppy3type(c, f):
    if c.uae_floppy3type.explicit:
        value = c.uae_floppy3type.explicit
    elif int(c.floppy_drive_count) > 3:
        value = c.int_default_floppy_type
    else:
        value = "-1"
    c.uae_floppy3type = value


# noinspection PyUnusedLocal,SpellCheckingInspection,PyUnresolvedReferences
def _uae_fpu_model(c, f):
    if c.uae_fpu_model.explicit:
        value = c.uae_fpu_model.explicit
    elif c.fpu == "0":
        value = "0"
    elif c.fpu == "68881":
        value = "68881"
    elif c.fpu == "68882":
        value = "68882"
    elif c.fpu == "68040":
        value = "68040"
    elif c.fpu == "68060":
        value = "68060"
    else:
        f.fail("Unknown FPU")
        raise Exception("Failed")
    c.uae_fpu_model = value


# noinspection PyUnusedLocal,SpellCheckingInspection,PyUnresolvedReferences
def _uae_gfxcard_size(c, f):
    t = c.uae_gfxcard_type
    if c.uae_gfxcard_size.explicit:
        value = c.uae_gfxcard_size.explicit
    elif t == "":
        value = "0"
    elif t == "PicassoII":
        value = "2"
    elif t == "PicassoII+":
        value = "2"
    elif t == "PicassoIV_Z2":
        value = "4"
    elif t == "PicassoIV_Z3":
        value = "4"
    elif t == "ZorroII":
        value = "4"
    elif t == "ZorroIII":
        value = "16"
    else:
        f.warning("Unrecognized graphics card: " + t)
        value = "0"
    c.uae_gfxcard_size = value


# noinspection PyUnusedLocal,SpellCheckingInspection,PyUnresolvedReferences
def _uae_gfxcard_type(c, f):
    t = c.graphics_card
    if c.uae_gfxcard_type.explicit:
        value = c.uae_gfxcard_type.explicit
    elif t == "":
        value = ""
    elif t == "uaegfx":
        if c.uae_cpu_24bit_addressing == "true":
            value = "ZorroII"
        else:
            value = "ZorroIII"
    elif t == "uaegfx-z2":
        value = "ZorroII"
    elif t == "uaegfx-z3":
        value = "ZorroIII"
    elif t == "picasso-ii":
        value = "PicassoII"
    elif t == "picasso-ii+":
        value = "PicassoII+"
    elif t == "picasso-iv":
        if c.uae_cpu_24bit_addressing == "true":
            value = "PicassoIV_Z2"
        else:
            value = "PicassoIV_Z3"
    elif t == "picasso-iv-z2":
        value = "PicassoIV_Z2"
    elif t == "picasso-iv-z3":
        value = "PicassoIV_Z3"
    # FIXME: cards are missing here
    else:
        f.warning("Unrecognized graphics card: " + t)
        value = ""
    c.uae_gfxcard_type = value


# noinspection PyUnusedLocal,SpellCheckingInspection,PyUnresolvedReferences
def _uae_joyport0(c, f):
    if c.uae_joyport0.explicit:
        f.warning("uae_joyport0 specified (use official options instead")


# noinspection PyUnusedLocal,SpellCheckingInspection,PyUnresolvedReferences
def _uae_joyport0autofire(c, f):
    if c.uae_joyport0autofire.explicit:
        f.warning("uae_joyport0autofire: use official options instead")


# noinspection PyUnusedLocal,SpellCheckingInspection,PyUnresolvedReferences
def _uae_joyport1(c, f):
    if c.uae_joyport1.explicit:
        f.warning("uae_joyport1 specified (use official options instead")


# noinspection PyUnusedLocal,SpellCheckingInspection,PyUnresolvedReferences
def _uae_joyport1autofire(c, f):
    if c.uae_joyport1autofire.explicit:
        f.warning("uae_joyport1autofire: use official options instead")


# noinspection PyUnusedLocal,SpellCheckingInspection,PyUnresolvedReferences
def _uae_mmu_model(c, f):
    if c.uae_mmu_model.explicit:
        value = c.uae_mmu_model.explicit
    elif c.cpu == "68000":
        value = "0"
    elif c.cpu == "68010":
        value = "0"
    elif c.cpu == "68EC020":
        value = "0"
    elif c.cpu == "68020":
        value = "0"
    elif c.cpu == "68EC030":
        value = "0"
    elif c.cpu == "68030":
        value = "68030"
    elif c.cpu == "68EC040":
        value = "0"
    elif c.cpu == "68LC040":
        value = "68040"
    elif c.cpu == "68040-NOMMU":
        value = "0"
    elif c.cpu == "68040":
        value = "68040"
    elif c.cpu == "68EC060":
        value = "0"
    elif c.cpu == "68LC060":
        value = "68060"
    elif c.cpu == "68060-NOMMU":
        value = "0"
    elif c.cpu == "68060":
        value = "68060"
    else:
        f.fail("Unknown CPU")
        raise Exception("Failed")
    c.uae_mmu_model = value


# noinspection PyUnusedLocal,SpellCheckingInspection,PyUnresolvedReferences
def _uae_native_code(c, f):
    if c.uae_native_code.explicit:
        value = c.uae_native_code.explicit
    elif c.uaenative_library == "1":
        value = "true"
    else:
        value = "false"
    c.uae_native_code = value


# noinspection PyUnusedLocal,SpellCheckingInspection,PyUnresolvedReferences
def _uae_ppc_model(c, f):
    pass


# noinspection PyUnusedLocal,SpellCheckingInspection,PyUnresolvedReferences
def _uae_rtc(c, f):
    # FIXME: Blizzard expansions!
    if c.uae_chipset_compatible == "-":
        if c.uae_rtc.explicit:
            value = c.uae_rtc.explicit
            if f.matches(value, "none"):
                value = "none"
            elif f.matches(value, "auto"):
                value = "none"
            elif f.matches(value, "MSM6242B"):
                value = "MSM6242B"
            elif f.matches(value, "MSM6242B_A2000"):
                value = "MSM6242B_A2000"
            elif f.matches(value, "RP5C01A"):
                value = "RP5C01A"
            else:
                f.warning(value + ": invalid value")
                value = "none"
        else:
            value = "none"
    else:
        if c.uae_rtc.explicit and c.uae_rtc.explicit != "auto":
            f.warning("uae_rtc is ignored (compatible chipset enabled)")
        if c.uae_chipset_compatible == "Generic":
            value = "RP5C01A"
        elif c.uae_chipset_compatible == "CDTV":
            value = "MSM6242B"
        elif c.uae_chipset_compatible == "CD32":
            value = "none"
        elif c.uae_chipset_compatible == "A500":
            if int(c.int_bogomem_size):
                value = "MSM6242B"
            elif int(c.int_chipmem_size) > 0x80000:
                value = "MSM6242B"
            elif int(c.int_fastmem_size):
                value = "MSM6242B"
            else:
                value = "none"
        elif c.uae_chipset_compatible == "A500+":
            value = "MSM6242B"
        elif c.uae_chipset_compatible == "A600":
            value = "none"
        elif c.uae_chipset_compatible == "A1000":
            value = "none"
        elif c.uae_chipset_compatible == "A1200":
            if int(c.int_fastmem_size) or int(c.int_z3fastmem_size):
                value = "MSM6242B"
            else:
                value = "none"
        elif c.uae_chipset_compatible == "A2000":
            value = "MSM6242B"
        elif c.uae_chipset_compatible == "A3000":
            value = "RP5C01A"
        elif c.uae_chipset_compatible == "A3000T":
            value = "RP5C01A"
        elif c.uae_chipset_compatible == "A4000":
            value = "RP5C01A"
        elif c.uae_chipset_compatible == "A4000T":
            value = "RP5C01A"
        else:
            f.fail("unknown uae_chipset_compatible")
            raise Exception("Failed")
    c.uae_rtc = value


# noinspection PyUnusedLocal,SpellCheckingInspection,PyUnresolvedReferences
def _uae_sana2(c, f):
    if c.uae_sana2.explicit:
        # FIXME: ok? keep already specified value
        value = c.uae_rtc.explicit
        # FIXME: match and normalize uae boolean
    else:
        value = "false"
    c.uae_sana2 = value


# noinspection PyUnusedLocal,SpellCheckingInspection,PyUnresolvedReferences
def _uae_slirp_implementation(c, f):
    if c.uae_slirp_implementation.explicit:
        # FIXME: ok? keep already specified value
        value = c.uae_slirp_implementation.explicit
        # FIXME: check value
    else:
        value = "auto"
    c.uae_slirp_implementation = value


# noinspection PyUnusedLocal,SpellCheckingInspection,PyUnresolvedReferences
def _uae_toccata(c, f):
    if c.uae_toccata.explicit:
        value = c.uae_toccata.explicit
        if f.matches(value, ["true", "yes", "1"]):
            value = "true"
        elif f.matches(value, ["false", "no", "0"]):
            value = "false"
        else:
            f.warning(value + ": invalid value")
            value = "false"
    elif c.sound_card == "toccata":
        value = "true"
    else:
        value = "false"
    c.uae_toccata = value


# noinspection PyUnusedLocal,SpellCheckingInspection,PyUnresolvedReferences
def _uae_z3chipmem_size(c, f):
    if c.uae_z3chipmem_size.explicit:
        value = c.uae_z3chipmem_size.explicit
    else:
        value = "0"
    c.uae_z3chipmem_size = value


# noinspection PyUnusedLocal,SpellCheckingInspection,PyUnresolvedReferences
def _uae_z3mem_size(c, f):
    if c.uae_z3mem_size.explicit:
        value = c.uae_z3mem_size.explicit
    elif c.zorro_iii_memory:
        value = str(int(c.zorro_iii_memory) // 1024)
    else:
        value = "0"
    c.uae_z3mem_size = value


# noinspection PyUnusedLocal,SpellCheckingInspection,PyUnresolvedReferences
def _uaegfx_card(c, f):
    if c.uaegfx_card.explicit:
        # FIXME: check boolean
        value = c.uaegfx_card.explicit
    else:
        value = ""
    c.uaegfx_card = value


# noinspection PyUnusedLocal,SpellCheckingInspection,PyUnresolvedReferences
def _uaenative_library(c, f):
    if c.uaenative_library.explicit:
        value = c.uaenative_library.explicit
    else:
        value = "0"
    c.uaenative_library = value


# noinspection PyUnusedLocal,SpellCheckingInspection,PyUnresolvedReferences
def _zorro_iii_memory(c, f):
    if c.zorro_iii_memory.explicit:
        value = c.zorro_iii_memory.explicit
    else:
        value = "0"
    c.zorro_iii_memory = value


class AbstractExpandFunctions:

    @staticmethod
    def matches(a, b):
        pass

    @staticmethod
    def fail(message):
        pass

    @staticmethod
    def warning(message):
        pass

    @staticmethod
    def lower(s):
        pass


def expand_config(c, f):
    assert isinstance(f, AbstractExpandFunctions)
    _amiga_model(c, f)
    _accelerator(c, f)
    _accelerator_memory(c, f)
    _bsdsocket_library(c, f)
    _cdrom_drive_0(c, f)
    _cdrom_image_0(c, f)
    _int_model(c, f)
    _cdrom_drive_count(c, f)
    _chip_memory(c, f)
    _cpu(c, f)
    _dongle_type(c, f)
    _fast_memory(c, f)
    _floppy_drive_0(c, f)
    _floppy_drive_1(c, f)
    _floppy_drive_2(c, f)
    _floppy_drive_3(c, f)
    _platform(c, f)
    _floppy_drive_count(c, f)
    _floppy_drive_speed(c, f)
    _fpu(c, f)
    _freezer_cartridge(c, f)
    _graphics_card(c, f)
    _uae_cpu_24bit_addressing(c, f)
    _uae_gfxcard_type(c, f)
    _uae_gfxcard_size(c, f)
    _graphics_memory(c, f)
    _uae_cpuboard_type(c, f)
    _int_accelerator_name(c, f)
    _slow_memory(c, f)
    _int_bogomem_size(c, f)
    _int_chipmem_size(c, f)
    _uae_chipset(c, f)
    _int_chipset_name(c, f)
    _uae_cpu_model(c, f)
    _uae_fpu_model(c, f)
    _uae_mmu_model(c, f)
    _int_cpu_name(c, f)
    _int_cpuboardmem1_size(c, f)
    _int_default_floppy_type(c, f)
    _int_fastmem_size(c, f)
    _int_graphics_card_bus(c, f)
    _int_graphics_card_name(c, f)
    _int_kickstart_ext_sha1(c, f)
    _int_kickstart_sha1(c, f)
    _int_kickstart_revision(c, f)
    _int_kickstart_version(c, f)
    _motherboard_ram(c, f)
    _uae_a3000mem_size(c, f)
    _int_mbresmem_low_size(c, f)
    _int_model_name(c, f)
    _int_ppc_model(c, f)
    _zorro_iii_memory(c, f)
    _uae_z3mem_size(c, f)
    _int_z3fastmem_size(c, f)
    _uae_bsdsocket_emu(c, f)
    _uae_chipset_compatible(c, f)
    _uae_rtc(c, f)
    _uae_sana2(c, f)
    _uae_z3chipmem_size(c, f)
    _int_uae_boot_rom(c, f)
    _int_z3chipmem_size(c, f)
    _jit_compiler(c, f)
    _joystick_port_0_mode(c, f)
    _joystick_port_1_mode(c, f)
    _joystick_port_2_mode(c, f)
    _joystick_port_3_mode(c, f)
    _kickstart_file(c, f)
    _kickstart_ext_file(c, f)
    _network_card(c, f)
    _sound_card(c, f)
    _uae_a2065(c, f)
    _uae_bogomem_size(c, f)
    _uae_cd32cd(c, f)
    _uae_cd32fmv(c, f)
    _uae_chipmem_size(c, f)
    _uae_fastmem_size(c, f)
    _uae_floppy0(c, f)
    _uae_floppy0type(c, f)
    _uae_floppy1(c, f)
    _uae_floppy1type(c, f)
    _uae_floppy2(c, f)
    _uae_floppy2type(c, f)
    _uae_floppy3(c, f)
    _uae_floppy3type(c, f)
    _uae_joyport0(c, f)
    _uae_joyport0autofire(c, f)
    _uae_joyport1(c, f)
    _uae_joyport1autofire(c, f)
    _uaenative_library(c, f)
    _uae_native_code(c, f)
    _uae_ppc_model(c, f)
    _uae_slirp_implementation(c, f)
    _uae_toccata(c, f)
    _uaegfx_card(c, f)
