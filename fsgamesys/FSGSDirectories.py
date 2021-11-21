import logging
import os
import warnings
from configparser import ConfigParser
from functools import lru_cache
from typing import Dict, List, Optional

import fsboot
from fsbc.paths import Paths
from fsbc.user import get_common_documents_dir, get_documents_dir
from fscore.settings import Settings
from fscore.system import System
from fsgamesys.product import Product


class FSGSDirectories(object):
    _initialized = False

    @classmethod
    def initialize(cls) -> None:
        warnings.warn(
            "FSGSDirectories.initialize is deprecated", DeprecationWarning
        )
        logging.debug("[DEPRECATED] FSGSDirectories.initialize")
        cls._initialize()

    @classmethod
    def _initialize(cls) -> None:
        if hasattr(cls, "_initialized") and cls._initialized:
            return
        logging.debug("FSGSDirectories._initialize")
        cls.get_base_dir()
        cls._initialized = True

    @classmethod
    @lru_cache()
    def get_base_dir(cls) -> str:
        path = fsboot.base_dir()
        # Configuration and file database depends on path normalization,
        # especially for cross-platform portable mode.
        path = Paths.get_real_case(path)
        print("FSGSDirectories.get_base_dir =", repr(path))
        return path

    @classmethod
    @lru_cache()
    def portable_config(cls) -> Dict[str, str]:
        portable_ini = os.path.join(cls.get_base_dir(), "Portable.ini")
        if os.path.exists(portable_ini):
            cp = ConfigParser()
            cp.read(portable_ini, encoding="UTF-8")
            if cp.has_section("directories"):
                return {k: v for (k, v) in cp.items("directories")}
        return {}

    @classmethod
    @lru_cache()
    def portable_dir(cls, name: str) -> Optional[str]:
        config = cls.portable_config()
        try:
            path = config[name]
        except KeyError:
            return None
        return os.path.join(cls.get_base_dir(), path)

    @classmethod
    @lru_cache()
    def get_configurations_dir(cls) -> str:
        path = cls.portable_dir("configurations_dir")
        if not path:
            if Product.is_fs_uae():
                path = os.path.join(cls.get_base_dir(), "Configurations")
            else:
                path = os.path.join(cls.get_data_dir(), "Configs")
        if not os.path.exists(path):
            os.makedirs(path)
        path = Paths.get_real_case(path)
        return path

    @classmethod
    @lru_cache()
    def get_controllers_dir(cls) -> str:
        path = cls.portable_dir("controllers_dir")
        if not path:
            if Product.is_fs_uae():
                path = os.path.join(cls.get_base_dir(), "Controllers")
            else:
                path = os.path.join(cls.get_data_dir(), "Devs", "Joysticks")
        if not os.path.exists(path):
            os.makedirs(path)
        path = Paths.get_real_case(path)
        return path

    @classmethod
    @lru_cache()
    def get_kickstarts_dir(cls) -> str:
        path = cls.portable_dir("kickstarts_dir")
        if not path:
            if Product.is_fs_uae():
                path = os.path.join(cls.get_base_dir(), "Kickstarts")
            else:
                path = os.path.join(cls.media_dir(), "ROMs")
        if not os.path.exists(path):
            os.makedirs(path)
        path = Paths.get_real_case(path)
        return path

    @classmethod
    @lru_cache()
    def downloads_dir(cls) -> str:
        path = cls.portable_dir("downloads_dir")
        if not path:
            path = os.path.join(cls.get_base_dir(), "Downloads")
        if not os.path.exists(path):
            os.makedirs(path)
        path = Paths.get_real_case(path)
        return path

    @classmethod
    def ensure_downloads_dir(cls) -> str:
        path = cls.downloads_dir()
        if not os.path.exists(path):
            os.makedirs(path)
        return path

    @classmethod
    @lru_cache()
    def get_floppies_dir(cls) -> str:
        path = cls.portable_dir("floppies_dir")
        if not path:
            if Product.is_fs_uae():
                path = os.path.join(cls.get_base_dir(), "Floppies")
            else:
                path = os.path.join(cls.media_dir(), "Floppies")
        if not os.path.exists(path):
            os.makedirs(path)
        path = Paths.get_real_case(path)
        return path

    @classmethod
    @lru_cache()
    def get_hard_drives_dir(cls) -> str:
        path = cls.portable_dir("hard_drives_dir")
        if not path:
            if Product.is_fs_uae():
                path = os.path.join(cls.get_base_dir(), "Hard Drives")
            else:
                path = os.path.join(cls.media_dir(), "HardDrives")
        if not os.path.exists(path):
            os.makedirs(path)
        path = Paths.get_real_case(path)
        return path

    @classmethod
    @lru_cache()
    def get_cdroms_dir(cls) -> str:
        path = cls.portable_dir("cdroms_dir")
        if not path:
            if Product.is_fs_uae():
                path = os.path.join(cls.get_base_dir(), "CD-ROMs")
            else:
                path = os.path.join(cls.media_dir(), "CD-ROMs")
        if not os.path.exists(path):
            os.makedirs(path)
        path = Paths.get_real_case(path)
        return path

    @classmethod
    @lru_cache()
    def get_logs_dir(cls) -> str:
        path = cls.portable_dir("logs_dir")
        if not path:
            path = os.path.join(cls.get_cache_dir(), "Logs")
        if not os.path.exists(path):
            os.makedirs(path)
        path = Paths.get_real_case(path)
        return path

    @classmethod
    @lru_cache()
    def get_data_dir(cls) -> str:
        path = cls.portable_dir("data_dir")
        if not path:
            path = os.path.join(cls.get_base_dir(), "Data")
        if not os.path.exists(path):
            os.makedirs(path)
        path = Paths.get_real_case(path)
        return path

    @classmethod
    @lru_cache()
    def databases_dir(cls) -> str:
        path = os.path.join(cls.get_data_dir(), "Databases")
        if not os.path.exists(path):
            os.makedirs(path)
        return path

    @classmethod
    @lru_cache()
    def images_dir(cls) -> str:
        path = os.path.join(cls.get_data_dir(), "Images")
        if not os.path.exists(path):
            os.makedirs(path)
        return path

    @classmethod
    @lru_cache()
    def media_dir(cls) -> str:
        path = cls.portable_dir("media_dir")
        if not path:
            path = os.path.join(cls.get_base_dir(), "Media")
        if not os.path.exists(path):
            os.makedirs(path)
        path = Paths.get_real_case(path)
        return path

    @classmethod
    @lru_cache()
    def images_dir_for_sha1(cls, sha1: str) -> str:
        path = os.path.join(cls.images_dir(), sha1[:2])
        # if not os.path.exists(path):
        #     os.makedirs(path)
        return path

    @classmethod
    @lru_cache()
    def get_launcher_dir(cls) -> str:
        return cls.get_data_dir()

    @classmethod
    @lru_cache()
    def get_titles_dir(cls) -> str:
        path = cls.portable_dir("titles_dir")
        if not path:
            if Product.is_fs_uae():
                path = os.path.join(cls.get_base_dir(), "Titles")
            else:
                path = os.path.join(cls.get_data_dir(), "Titles")
        return path

    @classmethod
    @lru_cache()
    def saves_dir(cls) -> str:
        path = cls.portable_dir("saves_dir")
        if not path:
            path = os.path.join(cls.get_data_dir(), "Saves")
        if not os.path.exists(path):
            os.makedirs(path)
        path = Paths.get_real_case(path)
        return path

    @classmethod
    @lru_cache()
    def get_save_states_dir(cls) -> str:
        return cls.saves_dir()

        # # path = cls.portable_dir("save_states_dir")
        # path = cls.portable_dir("saves_dir")
        # if not path:
        #     # if openretro:
        #     path = os.path.join(cls.get_data_dir(), "Saves")
        #     # else:
        #     #     path = os.path.join(cls.get_base_dir(), "Save States")
        # if not os.path.exists(path):
        #     os.makedirs(path)
        # path = Paths.get_real_case(path)
        # return path

    @classmethod
    @lru_cache()
    def screenshots_output_dir(cls) -> str:
        path: Optional[str] = Settings.get("screenshots_output_dir")
        if not path:
            path = cls.portable_dir("screenshots_output_dir")
        if not path:
            path = os.path.join(get_documents_dir(), "Screenshots")
        if not os.path.exists(path):
            os.makedirs(path)
        return path

    @classmethod
    @lru_cache()
    def get_screenshots_dir(cls) -> str:
        path = cls.portable_dir("screenshots_dir")
        if not path:
            if Product.is_fs_uae():
                path = os.path.join(cls.get_base_dir(), "Screenshots")
            else:
                path = os.path.join(cls.get_data_dir(), "Screenshots")
        return path

    @classmethod
    @lru_cache()
    def get_images_dir(cls) -> str:
        cls._initialize()
        path = cls.get_base_dir()
        return path

    @classmethod
    @lru_cache()
    def get_covers_dir(cls) -> str:
        path = cls.portable_dir("covers_dir")
        if not path:
            if Product.is_fs_uae():
                path = os.path.join(cls.get_base_dir(), "Covers")
            else:
                path = os.path.join(cls.get_data_dir(), "Covers")
        return path

    @classmethod
    @lru_cache()
    def get_themes_dir(cls) -> str:
        path = cls.portable_dir("themes_dir")
        if not path:
            if Product.is_fs_uae():
                path = os.path.join(cls.get_base_dir(), "Themes")
            else:
                path = os.path.join(cls.get_data_dir(), "Themes")
        if not os.path.exists(path):
            os.makedirs(path)
        return path

    @classmethod
    def get_plugins_dir(cls):
        return cls.get_system_dir()

    @classmethod
    @lru_cache()
    def get_system_dir(cls):
        path = os.path.join(cls.get_base_dir(), "System")
        if not os.path.exists(path):
            os.makedirs(path)
        return path

    @classmethod
    @lru_cache()
    def get_cache_dir(cls) -> str:
        path = cls.portable_dir("cache_dir")
        if not path:
            path = os.path.join(cls.get_base_dir(), "Cache")
        if not os.path.exists(path):
            os.makedirs(path)
        if not os.path.exists(os.path.join(path, ".nobackup")):
            open(os.path.join(path, ".nobackup"), "w").close()
        return path

    @classmethod
    @lru_cache()
    def get_files_dirs(cls) -> List[str]:
        paths = [cls.get_floppies_dir(), cls.get_cdroms_dir()]
        return paths

    @classmethod
    @lru_cache()
    def get_titles_dirs(cls) -> List[str]:
        paths = [cls.get_titles_dir()]
        return paths

    @classmethod
    @lru_cache()
    def get_screenshots_dirs(cls) -> List[str]:
        paths = [cls.get_screenshots_dir()]
        return paths

    @classmethod
    @lru_cache()
    def get_images_dirs(cls) -> List[str]:
        paths = [cls.get_images_dir()]
        return paths

    @classmethod
    @lru_cache()
    def get_covers_dirs(cls) -> List[str]:
        paths = [cls.get_covers_dir()]
        return paths

    @classmethod
    @lru_cache()
    def get_themes_dirs(cls) -> List[str]:
        paths = [cls.get_themes_dir()]
        return paths

    @classmethod
    def get_amiga_forever_directories(cls) -> List[str]:
        paths: List[str] = []
        if fsboot.is_portable():
            # Portable version, don't try to find ROM files outside the
            # portable directory by default.
            pass
        else:
            if System.windows:
                path = get_common_documents_dir()
                path = os.path.join(path, "Amiga Files")
                if os.path.exists(path):
                    paths.append(path)
            else:
                path = os.path.expanduser(
                    "~/.wine/drive_c/users/Public/Documents/Amiga Files"
                )
                if os.path.exists(path):
                    paths.append(path)
        path = cls.get_base_dir()
        path = os.path.join(path, "AmigaForever", "Amiga Files")
        if os.path.exists(path):
            paths.append(path)
        return paths

    @classmethod
    def get_default_search_path(cls) -> List[str]:
        paths: List[str] = []
        path = cls.get_base_dir()
        paths.append(path)
        if Product.includes_amiga():
            for path in cls.get_amiga_forever_directories():
                paths.append(path)
        return paths
