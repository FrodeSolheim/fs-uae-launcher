import os
import sys
import traceback
from fsbc.Application import app, Application
import fsbc.fs as fs
from fsbc.Paths import Paths
from fsbc.user import get_home_dir, get_documents_dir
from fsbc.user import get_common_documents_dir
from fsbc.util import memoize
from fsbc.system import windows


class FSGSDirectories(object):

    base_dir = ""
    initialized = False

    @classmethod
    def initialize(cls):
        if cls.initialized:
            return
        cls.initialized = True
        for arg in sys.argv[1:]:
            if arg.startswith("--"):
                if "=" in arg:
                    key, value = arg[2:].split("=", 1)
                    key = key.replace("-", "_")
                    if key == "base_dir":
                        value = os.path.abspath(value)
                        print("setting base_dir")
                        cls.base_dir = value
        if cls.base_dir:
            print(
                "base_dir was specified so we will not check for "
                "portable dir")
        else:
            cls.setup_portable()
        if not cls.base_dir:
            print("base_dir not decided yet, checking FS_UAE_BASE_DIR")
            if "FS_UAE_BASE_DIR" in os.environ and \
                    os.environ["FS_UAE_BASE_DIR"]:
                print("base dir specified by FS_UAE_BASE_DIR")
                cls.base_dir = os.environ["FS_UAE_BASE_DIR"]
        if cls.base_dir:
            print("base dir is", cls.base_dir)
            try:
                cls.base_dir = Paths.get_real_case(cls.base_dir)
            except:
                traceback.print_exc()
                print("WARNING: error looking up real case for base dir")
            print("base dir (normalized) is", cls.base_dir)
        else:
            print("using default base_dir")

    @classmethod
    def setup_portable(cls):
        path = Application.executable_dir()
        # path = os.path.dirname(os.path.abspath(sys.executable))
        last = ""
        while not last == path:
            portable_ini_path = os.path.join(path, "Portable.ini")
            print("checking", portable_ini_path)
            if os.path.exists(portable_ini_path):
                print("detected portable dir", path)
                cls.base_dir = path
                return
            last = path
            path = os.path.dirname(path)
        print("no Portable.ini found in search path")

    @classmethod
    def read_custom_path(cls, name):
        for app_name in ["fs-uae-launcher", "fs-uae"]:
            key_path = os.path.join(fs.get_app_config_dir(app_name), name)
            print("- checking", key_path)
            if os.path.exists(key_path):
                try:
                    with open(key_path, "r", encoding="UTF-8") as f:
                        path = f.read().strip()
                        break
                except Exception as e:
                    print("error reading custom path", repr(e))
        else:
            return None
        path_lower = path.lower()
        if path_lower.startswith("$home/") or path_lower.startswith("$home\\"):
            path = os.path.join(get_home_dir(), path[6:])
        return path

    @classmethod
    def get_base_dir(cls):
        cls.initialize()
        path = cls.base_dir
        if path:
            return path
        return cls._get_base_dir()

    @classmethod
    @memoize
    def _get_base_dir(cls):
        path = cls.read_custom_path("base-dir")
        if not path:
            path = os.path.join(get_documents_dir(True), "FS-UAE")
        if not os.path.exists(path):
            os.makedirs(path)
        path = Paths.get_real_case(path)
        print("base dir is", path)
        return path

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
        return paths

    @classmethod
    def get_whdload_dir(cls):
        path = os.path.join(cls.get_hard_drives_dir(), "WHDLoad")
        if os.path.exists(path):
            path = Paths.get_real_case(path)
            return path
        return None

    @classmethod
    def get_configurations_dir(cls):
        path = os.path.join(cls.get_base_dir(), "Configurations")
        if not os.path.exists(path):
            os.makedirs(path)
        path = Paths.get_real_case(path)
        return path

    @classmethod
    def get_controllers_dir(cls):
        path = os.path.join(cls.get_base_dir(), "Controllers")
        if not os.path.exists(path):
            os.makedirs(path)
        path = Paths.get_real_case(path)
        return path

    @classmethod
    def get_kickstarts_dir(cls):
        path = os.path.join(cls.get_base_dir(), "Kickstarts")
        if not os.path.exists(path):
            os.makedirs(path)
        path = Paths.get_real_case(path)
        return path

    @classmethod
    def get_downloads_dir(cls):
        path = os.path.join(cls.get_base_dir(), "Downloads")
        if not os.path.exists(path):
            os.makedirs(path)
        path = Paths.get_real_case(path)
        return path

    @classmethod
    def get_floppies_dir(cls):
        path = os.path.join(cls.get_base_dir(), "Floppies")
        if not os.path.exists(path):
            os.makedirs(path)
        path = Paths.get_real_case(path)
        return path

    @classmethod
    def get_hard_drives_dir(cls):
        path = os.path.join(cls.get_base_dir(), "Hard Drives")
        if not os.path.exists(path):
            os.makedirs(path)
        path = Paths.get_real_case(path)
        return path

    @classmethod
    def get_cdroms_dir(cls):
        path = os.path.join(cls.get_base_dir(), "CD-ROMs")
        if not os.path.exists(path):
            os.makedirs(path)
        path = Paths.get_real_case(path)
        return path

    @classmethod
    def get_logs_dir(cls):
        path = os.path.join(cls.get_cache_dir(), "Logs")
        if not os.path.exists(path):
            os.makedirs(path)
        path = Paths.get_real_case(path)
        return path

    @classmethod
    def get_data_dir(cls):
        path = os.path.join(cls.get_base_dir(), "Data")
        if not os.path.exists(path):
            os.makedirs(path)
        path = Paths.get_real_case(path)
        return path

    @classmethod
    def get_launcher_dir(cls):
        return cls.get_data_dir()

    @classmethod
    def get_titles_dir(cls):
        path = os.path.join(cls.get_base_dir(), "Titles")
        return path

    @classmethod
    def get_save_states_dir(cls):
        path = os.path.join(cls.get_base_dir(), "Save States")
        if not os.path.exists(path):
            os.makedirs(path)
        path = Paths.get_real_case(path)
        return path

    @classmethod
    def screenshots_output_dir(cls):
        path = app.settings["screenshots_output_dir"]
        if not path:
            path = os.path.join(get_documents_dir(), "Screenshots")
        if not os.path.exists(path):
            os.makedirs(path)
        return path

    @classmethod
    def get_screenshots_dir(cls):
        path = os.path.join(cls.get_base_dir(), "Screenshots")
        return path

    @classmethod
    def get_images_dir(cls):
        path = cls.get_base_dir()
        return path

    @classmethod
    def get_covers_dir(cls):
        path = os.path.join(cls.get_base_dir(), "Covers")
        return path

    @classmethod
    def get_themes_dir(cls):
        path = os.path.join(cls.get_base_dir(), "Themes")
        if not os.path.exists(path):
            os.makedirs(path)
        return path

    @classmethod
    def get_plugins_dir(cls):
        path = os.path.join(cls.get_base_dir(), "Plugins")
        if not os.path.exists(path):
            return None
        return path

    @classmethod
    def get_cache_dir(cls):
        path = os.path.join(cls.get_base_dir(), "Cache")
        if not os.path.exists(path):
            os.makedirs(path)
        if not os.path.exists(os.path.join(path, ".nobackup")):
            open(os.path.join(path, ".nobackup"), "w").close()
        return path

    @classmethod
    def get_files_dirs(cls):
        paths = [
            cls.get_floppies_dir(),
            cls.get_cdroms_dir(),
        ]
        return paths

    @classmethod
    def get_titles_dirs(cls):
        paths = [
            cls.get_titles_dir(),
        ]
        return paths

    @classmethod
    def get_screenshots_dirs(cls):
        paths = [
            cls.get_screenshots_dir(),
        ]
        return paths

    @classmethod
    def get_images_dirs(cls):
        paths = [
            cls.get_images_dir(),
        ]
        return paths

    @classmethod
    def get_covers_dirs(cls):
        paths = [
            cls.get_covers_dir(),
        ]
        return paths

    @classmethod
    def get_themes_dirs(cls):
        paths = [cls.get_themes_dir()]
        return paths
