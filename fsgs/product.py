FSGS_PRODUCT_FS_UAE_LAUNCHER = 0
FSGS_PRODUCT_OPENRETRO_LAUNCHER = 1
FSGS_PRODUCT_OPENRETRO_C64 = 2

_fsgs_product = FSGS_PRODUCT_FS_UAE_LAUNCHER


def fsgs_product():
    return _fsgs_product


def fsgs_product_fs_uae_clauncher():
    return _fsgs_product == FSGS_PRODUCT_FS_UAE_LAUNCHER


def fsgs_product_openretro_clauncher():
    return _fsgs_product == FSGS_PRODUCT_OPENRETRO_LAUNCHER


def fsgs_product_openretro_c64():
    return _fsgs_product == FSGS_PRODUCT_OPENRETRO_C64
