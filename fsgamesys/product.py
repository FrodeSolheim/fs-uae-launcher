PLATFORM_AMIGA = "amiga"
PLATFORM_SPECTRUM = "spectrum"


class Product:

    base_name = "FS-UAE"
    default_platform_id = PLATFORM_AMIGA

    @classmethod
    def includes_amiga(cls) -> bool:
        return cls.base_name in ["FS-UAE", "OpenRetro"]

    @classmethod
    def is_fs_fuse(cls) -> bool:
        return cls.base_name == "FS-Fuse"

    @classmethod
    def is_fs_uae(cls) -> bool:
        return cls.base_name == "FS-UAE"

    @classmethod
    def is_openretro(cls) -> bool:
        return cls.base_name == "OpenRetro"

    @classmethod
    def getLauncherPluginName(cls) -> str:
        return f"{cls.base_name}-Launcher"
