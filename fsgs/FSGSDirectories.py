import os

import functools
from configparser import ConfigParser

import fsboot
from fsbc.paths import Paths
from fsbc.settings import Settings
from fsbc.system import windows, macosx
from fsbc.user import get_common_documents_dir
from fsbc.user import get_documents_dir


class FSGSDirectories(object):
    @classmethod
    def initialize(cls):
        print("[DEPRECATED] FSGSDirectories.initialize")
        cls._initialize()

    @classmethod
    def _initialize(cls):
        if hasattr(cls, "_initialized") and cls._initialized:
            return
        print("FSGSDirectories._initialize")
        cls.get_base_dir()
        cls._initialized = True

    @classmethod
    @functools.lru_cache()
    def get_base_dir(cls):
        path = fsboot.base_dir()
        # Configuration and file database depends on path normalization,
        # especially for cross-platform portable mode.
        path = Paths.get_real_case(path)
        return path

    @classmethod
    @functools.lru_cache()
    def portable_config(cls):
        portable_ini = os.path.join(cls.get_base_dir(), "Portable.ini")
        if os.path.exists(portable_ini):
            cp = ConfigParser()
            cp.read(portable_ini, encoding="UTF-8")
            if cp.has_section("directories"):
                return {k: v for (k, v) in cp.items("directories")}
        return {}

    @classmethod
    @functools.lru_cache()
    def portable_dir(cls, name):
        config = cls.portable_config()
        try:
            path = config[name]
        except KeyError:
            return None
        return os.path.join(cls.get_base_dir(), path)

    @classmethod
    @functools.lru_cache()
    def get_configurations_dir(cls):
        path = cls.portable_dir("configurations_dir")
        if not path:
            path = os.path.join(cls.get_base_dir(), "Configurations")
        if not os.path.exists(path):
            os.makedirs(path)
        path = Paths.get_real_case(path)
        return path

    @classmethod
    @functools.lru_cache()
    def get_controllers_dir(cls):
        path = cls.portable_dir("controllers_dir")
        if not path:
            path = os.path.join(cls.get_base_dir(), "Controllers")
        if not os.path.exists(path):
            os.makedirs(path)
        path = Paths.get_real_case(path)
        return path

    @classmethod
    @functools.lru_cache()
    def get_kickstarts_dir(cls):
        path = cls.portable_dir("kickstarts_dir")
        if not path:
            path = os.path.join(cls.get_base_dir(), "Kickstarts")
        if not os.path.exists(path):
            os.makedirs(path)
        path = Paths.get_real_case(path)
        return path

    @classmethod
    @functools.lru_cache()
    def downloads_dir(cls):
        path = cls.portable_dir("downloads_dir")
        if not path:
            path = os.path.join(cls.get_base_dir(), "Downloads")
        if not os.path.exists(path):
            os.makedirs(path)
        path = Paths.get_real_case(path)
        return path

    @classmethod
    def ensure_downloads_dir(cls):
        path = cls.downloads_dir()
        if not os.path.exists(path):
            os.makedirs(path)
        return path

    @classmethod
    @functools.lru_cache()
    def get_floppies_dir(cls):
        path = cls.portable_dir("floppies_dir")
        if not path:
            path = os.path.join(cls.get_base_dir(), "Floppies")
        if not os.path.exists(path):
            os.makedirs(path)
        path = Paths.get_real_case(path)
        return path

    @classmethod
    @functools.lru_cache()
    def get_hard_drives_dir(cls):
        path = cls.portable_dir("hard_drives_dir")
        if not path:
            path = os.path.join(cls.get_base_dir(), "Hard Drives")
        if not os.path.exists(path):
            os.makedirs(path)
        path = Paths.get_real_case(path)
        return path

    @classmethod
    @functools.lru_cache()
    def get_cdroms_dir(cls):
        path = cls.portable_dir("cdroms_dir")
        if not path:
            path = os.path.join(cls.get_base_dir(), "CD-ROMs")
        if not os.path.exists(path):
            os.makedirs(path)
        path = Paths.get_real_case(path)
        return path

    @classmethod
    @functools.lru_cache()
    def get_logs_dir(cls):
        path = cls.portable_dir("logs_dir")
        if not path:
            path = os.path.join(cls.get_cache_dir(), "Logs")
        if not os.path.exists(path):
            os.makedirs(path)
        path = Paths.get_real_case(path)
        return path

    @classmethod
    @functools.lru_cache()
    def get_data_dir(cls):
        path = cls.portable_dir("data_dir")
        if not path:
            path = os.path.join(cls.get_base_dir(), "Data")
        if not os.path.exists(path):
            os.makedirs(path)
        path = Paths.get_real_case(path)
        return path

    @classmethod
    @functools.lru_cache()
    def databases_dir(cls):
        path = os.path.join(cls.get_data_dir(), "Databases")
        if not os.path.exists(path):
            os.makedirs(path)
        return path

    @classmethod
    @functools.lru_cache()
    def images_dir(cls):
        path = os.path.join(cls.get_data_dir(), "Images")
        if not os.path.exists(path):
            os.makedirs(path)
        return path

    @classmethod
    @functools.lru_cache()
    def images_dir_for_sha1(cls, sha1):
        path = os.path.join(cls.images_dir(), sha1[:2])
        # if not os.path.exists(path):
        #     os.makedirs(path)
        return path

    @classmethod
    @functools.lru_cache()
    def get_launcher_dir(cls):
        return cls.get_data_dir()

    @classmethod
    @functools.lru_cache()
    def get_titles_dir(cls):
        path = cls.portable_dir("titles_dir")
        if not path:
            path = os.path.join(cls.get_base_dir(), "Titles")
        return path

    @classmethod
    @functools.lru_cache()
    def get_save_states_dir(cls):
        path = cls.portable_dir("save_states_dir")
        if not path:
            path = os.path.join(cls.get_base_dir(), "Save States")
        if not os.path.exists(path):
            os.makedirs(path)
        path = Paths.get_real_case(path)
        return path

    @classmethod
    @functools.lru_cache()
    def screenshots_output_dir(cls):
        path = Settings.instance()["screenshots_output_dir"]
        if not path:
            path = cls.portable_dir("screenshots_output_dir")
        if not path:
            path = os.path.join(get_documents_dir(), "Screenshots")
        if not os.path.exists(path):
            os.makedirs(path)
        return path

    @classmethod
    @functools.lru_cache()
    def get_screenshots_dir(cls):
        path = cls.portable_dir("screenshots_dir")
        if not path:
            path = os.path.join(cls.get_base_dir(), "Screenshots")
        return path

    @classmethod
    @functools.lru_cache()
    def get_images_dir(cls):
        cls._initialize()
        path = cls.get_base_dir()
        return path

    @classmethod
    @functools.lru_cache()
    def get_covers_dir(cls):
        path = cls.portable_dir("covers_dir")
        if not path:
            path = os.path.join(cls.get_base_dir(), "Covers")
        return path

    @classmethod
    @functools.lru_cache()
    def get_themes_dir(cls):
        path = cls.portable_dir("themes_dir")
        if not path:
            path = os.path.join(cls.get_base_dir(), "Themes")
        if not os.path.exists(path):
            os.makedirs(path)
        return path

    @classmethod
    @functools.lru_cache()
    def get_plugins_dir(cls):
        path = cls.portable_dir("plugins_dir")
        if not path:
            path = os.path.join(cls.get_base_dir(), "Plugins")
        if not os.path.exists(path):
            os.makedirs(path)
        return path

    @classmethod
    @functools.lru_cache()
    def get_cache_dir(cls):
        path = cls.portable_dir("cache_dir")
        if not path:
            path = os.path.join(cls.get_base_dir(), "Cache")
        if not os.path.exists(path):
            os.makedirs(path)
        if not os.path.exists(os.path.join(path, ".nobackup")):
            open(os.path.join(path, ".nobackup"), "w").close()
        return path

    @classmethod
    @functools.lru_cache()
    def get_files_dirs(cls):
        paths = [
            cls.get_floppies_dir(),
            cls.get_cdroms_dir(),
        ]
        return paths

    @classmethod
    @functools.lru_cache()
    def get_titles_dirs(cls):
        paths = [
            cls.get_titles_dir(),
        ]
        return paths

    @classmethod
    @functools.lru_cache()
    def get_screenshots_dirs(cls):
        paths = [
            cls.get_screenshots_dir(),
        ]
        return paths

    @classmethod
    @functools.lru_cache()
    def get_images_dirs(cls):
        paths = [
            cls.get_images_dir(),
        ]
        return paths

    @classmethod
    @functools.lru_cache()
    def get_covers_dirs(cls):
        paths = [
            cls.get_covers_dir(),
        ]
        return paths

    @classmethod
    @functools.lru_cache()
    def get_themes_dirs(cls):
        paths = [cls.get_themes_dir()]
        return paths

    @classmethod
    def get_amiga_forever_directories(cls):
        paths = []
        if fsboot.is_portable():
            # Portable version, don't try to find ROM files outside the
            # portable directory by default.
            pass
        else:
            if windows:
                path = get_common_documents_dir()
                path = os.path.join(path, "Amiga Files")
                if os.path.exists(path):
                    paths.append(path)
            else:
                path = os.path.expanduser(
                    "~/.wine/drive_c/users/Public/Documents/Amiga Files")
                if os.path.exists(path):
                    paths.append(path)
        path = cls.get_base_dir()
        path = os.path.join(path, "AmigaForever", "Amiga Files")
        if os.path.exists(path):
            paths.append(path)
        return paths

    @classmethod
    def get_default_search_path(cls):
        paths = []
        path = cls.get_base_dir()
        paths.append(path)
        for path in cls.get_amiga_forever_directories():
            paths.append(path)
        return paths
