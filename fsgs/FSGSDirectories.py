import os

import functools
from configparser import ConfigParser

import fsboot
from fsbc.paths import Paths
from fsbc.settings import Settings
from fsbc.system import windows
from fsbc.user import get_common_documents_dir
from fsbc.user import get_documents_dir


class FSGSDirectories(object):

    CACHE_DIR = 'cache_dir'
    CDROMS_DIR = 'cdroms_dir'
    CONTROLLERS_DIR = 'controllers_dir'
    COVERS_DIR = 'Covers'
    DATA_DIR = 'data_dir'
    DATABASES_DIR = 'databases_dir'
    DOWNLOAD_DIR = 'download_dir'
    FLOPPIES_DIR = 'floppier_dir'
    KICKSTARTS_DIR = 'kickstarts_dir'
    HARD_DRIVES_DIR = 'hard_drives_dir'
    IMAGES_DIR = 'images_dir'
    LOGS_DIR = 'logs_dir'
    PLUGINS_DIR = 'plugins_dir'
    SAVE_STATES_DIR = 'save_states_dir'
    SCREENSHOTS_DIR = 'screenshots_dir'
    THEMES_DIR = 'themes_dir'
    TITLES_DIR = 'titles_dir'
    # TODO: grab these names from LauncherConfig.get("name_dir")
    DIRNAME_TO_REALPATH = {
        CDROMS_DIR: 'CD-ROMs',
        CACHE_DIR: 'Cache',
        CONTROLLERS_DIR: 'Controllers',
        COVERS_DIR: 'Covers',
        DATA_DIR: 'Data',
        DATABASES_DIR: 'Databases',
        DOWNLOAD_DIR: 'Downloads',
        FLOPPIES_DIR: 'Floppies',
        KICKSTARTS_DIR: 'Kickstarts',
        HARD_DRIVES_DIR: 'Hard Drives',
        IMAGES_DIR: 'Images',
        LOGS_DIR: 'Logs',
        PLUGINS_DIR: 'Plugins',
        SAVE_STATES_DIR: 'Save States',
        SCREENSHOTS_DIR: 'Screenshots',
        THEMES_DIR: 'Themes',
        TITLES_DIR: 'Titles',
    }

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
        # cls.portable_dir()
        cls._initialized = True

    @classmethod
    def get_base_dir(cls):
        return fsboot.base_dir()

    @classmethod
    def _get_real_dir(cls, dir_name):
        if dir_name not in cls.DIRNAME_TO_REALPATH:
            raise NotImplementedError(
                "'{}' not managed in {}".format(dir_name,
                                                cls.DIRNAME_TO_REALPATH))
        return (cls.portable_dir(dir_name) or
                os.path.join(cls.get_base_dir(),
                             cls.DIRNAME_TO_REALPATH[dir_name]))

    @classmethod
    def ensure_dir_exists(cls, dir_name):
        path = cls._get_real_dir(dir_name)
        if not os.path.exists(path):
            if dir_name == cls.CACHE_DIR:
                func = cls.get_cache_dir
            elif dir_name == cls.CDROMS_DIR:
                func = cls.get_cdroms_dir
            elif dir_name == cls.CONTROLLERS_DIR:
                func = cls.get_controllers_dir
            elif dir_name == cls.COVERS_DIR:
                func = cls.get_covers_dir
            elif dir_name == cls.DATA_DIR:
                func = cls.get_data_dir
            elif dir_name == cls.DATABASES_DIR:
                func = cls.databases_dir #  FIXME: does not respect naming scheme
            elif dir_name == cls.DOWNLOAD_DIR:
                func = cls.get_downloads_dir
            elif dir_name == cls.FLOPPIES_DIR:
                func = cls.get_floppies_dir
            elif dir_name == cls.KICKSTARTS_DIR:
                func = cls.get_kickstarts_dir
            elif dir_name == cls.HARD_DRIVES_DIR:
                func = cls.get_hard_drives_dir
            elif dir_name == cls.IMAGES_DIR:
                func = cls.get_images_dir
            elif dir_name == cls.LOGS_DIR:
                func = cls.get_logs_dir
            elif dir_name == cls.PLUGINS_DIR:
                func = cls.get_plugins_dir
            elif dir_name == cls.SAVE_STATES_DIR:
                func = cls.get_save_states_dir
            elif dir_name == cls.SCREENSHOTS_DIR:
                func = cls.get_screenshots_dir
            elif dir_name == cls.THEMES_DIR:
                func = cls.get_themes_dir
            elif dir_name == cls.TITLES_DIR:
                func = cls.get_titles_dir
            func.cache_clear()

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
    def get_whdload_dir(cls):
        cls._initialize()
        path = os.path.join(cls.get_hard_drives_dir(), "WHDLoad")
        if os.path.exists(path):
            path = Paths.get_real_case(path)
            return path
        return None

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
    def get_downloads_dir(cls):
        path = cls.portable_dir("downloads_dir")
        if not path:
            path = os.path.join(cls.get_base_dir(), "Downloads")
        if not os.path.exists(path):
            os.makedirs(path)
        path = Paths.get_real_case(path)
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
        # XXX: maybe missing cls.get_portable_dir("databases_dir")?
        path = os.path.join(cls.get_data_dir(), "Databases")
        if not os.path.exists(path):
            os.makedirs(path)
        path = Paths.get_real_case(path)
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

    # FIXME: redundant?
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
    # FIXME: missing "Images" dir?
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

    # FIXME: redundant?
    @classmethod
    @functools.lru_cache()
    def get_titles_dirs(cls):
        paths = [
            cls.get_titles_dir(),
        ]
        return paths

    # FIXME: redundant?
    @classmethod
    @functools.lru_cache()
    def get_screenshots_dirs(cls):
        paths = [
            cls.get_screenshots_dir(),
        ]
        return paths

    # FIXME: redundant?
    @classmethod
    @functools.lru_cache()
    def get_images_dirs(cls):
        paths = [
            cls.get_images_dir(),
        ]
        return paths

    # FIXME: redundant?
    @classmethod
    @functools.lru_cache()
    def get_covers_dirs(cls):
        paths = [
            cls.get_covers_dir(),
        ]
        return paths

    # FIXME: redundant?
    @classmethod
    @functools.lru_cache()
    def get_themes_dirs(cls):
        paths = [cls.get_themes_dir()]
        return paths

    @classmethod
    def get_default_search_path(cls):
        paths = []
        path = cls.get_base_dir()
        # if windows:
        #     path = path.replace("/", "\\")
        paths.append(path)

        if windows:
            path = get_common_documents_dir()
            path = os.path.join(path, "Amiga Files")
            if os.path.exists(path):
                paths.append(path)
        path = cls.get_base_dir()
        path = os.path.join(path, "AmigaForever", "Amiga Files")
        if os.path.exists(path):
            paths.append(path)
        return paths
