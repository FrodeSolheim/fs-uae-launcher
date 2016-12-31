import os
import ctypes
import functools
import getpass
import subprocess
import logging
import sys

# The current directory when the application was started.
_cwd = os.getcwd()
# Key-value store
values = {}
logger = logging.getLogger("BOOT")


def set(key, value):
    values[key] = value


def get(key, default=""):
    return values.get(key, default)


def setup_logging():
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    # formatter = logging.Formatter(
    #     "[%(name)s] - %(asctime)s - %(levelname)s - %(message)s")
    formatter = logging.Formatter("[%(name)s] %(message)s")
    ch.setFormatter(formatter)
    root.addHandler(ch)


if "--workspace" in sys.argv:
    # Hack
    set("fws", "1")
if "--logging" in sys.argv:
    setup_logging()
    sys.argv.remove("--logging")


@functools.lru_cache()
def executable_dir():
    logger.debug("executable_dir")
    logger.debug("sys.executable = %s", sys.executable)
    if "python" in os.path.basename(sys.executable):
        logger.debug("Using sys.argv[0] instead of python interpreter path")
        # We do not want the directory of the (installed) python
        # interpreter, but rather the main application script.
        logger.debug("sys.argv[0] = %s", repr(sys.argv[0]))
        path = os.path.dirname(sys.argv[0])
        logger.debug("%s", repr(path))
        path = os.path.join(os.getcwd(), path)
        logger.debug("%s", repr(path))
        path = os.path.normpath(path)
        logger.debug("%s", repr(path))
    else:
        path = os.path.dirname(sys.executable)
    logger.debug("executable_dir = %s", repr(path))
    return path


if sys.platform == "win32":
    S_OK = 0
    CSIDL_DESKTOP = 0
    CSIDL_PERSONAL = 5
    CSIDL_APPDATA = 26
    CSIDL_MYPICTURES = 39
    CSIDL_PROFILE = 40
    CSIDL_COMMON_DOCUMENTS = 46
    from ctypes import windll, wintypes
    _SHGetFolderPath = windll.shell32.SHGetFolderPathW
    _SHGetFolderPath.argtypes = [
        wintypes.HWND, ctypes.c_int, wintypes.HANDLE, wintypes.DWORD,
        wintypes.LPCWSTR]

    def csidl_dir(csidl):
        path_buf = ctypes.create_unicode_buffer(wintypes.MAX_PATH)
        result = _SHGetFolderPath(0, csidl, 0, 0, path_buf)
        if result != S_OK:
            raise RuntimeError(
                "Could not find common directory for CSIDL {}".format(csidl))
        return path_buf.value

    class WinPathsException(Exception):
        pass

    def err_unless_zero(result):
        if result == 0:
            return result
        else:
            raise WinPathsException(
                "Failed to retrieve windows path: %s" % result)

    _SHGetFolderPath.restype = err_unless_zero


@functools.lru_cache()
def user_name():
    name = getpass.getuser()
    return name


@functools.lru_cache()
def xdg_user_dir(name):
    try:
        process = subprocess.Popen(
                ["xdg-user-dir", name], stdout=subprocess.PIPE)
        path = process.stdout.read().strip()
        path = path.decode("UTF-8")
        logger.debug("XDG user dir %s => %s", name, repr(path))
    except Exception:
        path = None
    return path


@functools.lru_cache()
def home_dir():
    if sys.platform == "win32":
        path = csidl_dir(CSIDL_PROFILE)
    else:
        path = os.path.expanduser("~")
    assert isinstance(path, str)
    # path = unicode_path(path)
    return path


@functools.lru_cache()
def documents_dir(create=False):
    if sys.platform == "win32":
        path = csidl_dir(CSIDL_PERSONAL)
    elif sys.platform == "darwin":
        path = os.path.join(home_dir(), "Documents")
    else:
        path = xdg_user_dir("DOCUMENTS")
        if not path:
            path = home_dir()
    assert isinstance(path, str)
    # path = unicode_path(path)
    if create and not os.path.isdir(path):
        os.makedirs(path)
    return path


def is_portable():
    return portable_dir() is not None


@functools.lru_cache()
def portable_dir():
    path = executable_dir()
    last = ""
    while not last == path:
        portable_ini_path = os.path.join(path, "Portable.ini")
        logger.debug("Checking %s", repr(portable_ini_path))
        if os.path.exists(portable_ini_path):
            logger.debug("Detected portable dir: %s", repr(path))
            return path
        last = path
        path = os.path.dirname(path)
    logger.debug("No Portable.ini found in search path")
    return None


@functools.lru_cache()
def common_data_dir(create=False):
    if sys.platform == "win32":
        path = csidl_dir(CSIDL_APPDATA)
    elif sys.platform == "darwin":
        path = os.path.join(home_dir(), "Library", "Application Support")
    else:
        path = os.path.join(home_dir(), ".local", "share")
        path = os.environ.get("XDG_DATA_HOME", path)
    # path = unicode_path(path)
    if create and not os.path.exists(path):
        os.makedirs(path)
    return path


@functools.lru_cache()
def app_data_dir(app):
    return os.path.join(common_data_dir(), app)


@functools.lru_cache()
def app_config_dir(app):
    # if not app:
    #     app = get_app_id()
    if sys.platform == "win32":
        path = app_data_dir(app)
    elif sys.platform == "darwin":
        path = os.path.join(home_dir(), "Library", "Preferences", app)
    else:
        path = os.path.join(home_dir(), ".config")
        path = os.environ.get("XDG_CONFIG_HOME", path)
        path = os.path.join(path, app)
        # path = unicode_path(path)
    if not os.path.isdir(path):
        os.makedirs(path)
    return path


@functools.lru_cache()
def custom_path(name):
    for app_name in ["fs-uae-launcher", "fs-uae"]:
        key_path = os.path.join(app_config_dir(app_name), name)
        logger.debug("Checking %s", repr(key_path))
        if os.path.exists(key_path):
            try:
                with open(key_path, "r", encoding="UTF-8") as f:
                    path = f.read().strip()
                    break
            except Exception as e:
                logger.debug("Error reading custom path %s", repr(e))
    else:
        return None
    path_lower = path.lower()
    if path_lower.startswith("$home/") or path_lower.startswith("$home\\"):
        path = os.path.join(home_dir(), path[6:])
    return path


@functools.lru_cache()
def base_dir():
    logger.debug("Find base directory")
    for arg in sys.argv[1:]:
        if arg.startswith("--base-dir="):
            path = arg[11:]
            path = os.path.abspath(path)
            logger.debug("Base directory via argv: %s", repr(path))
            sys.argv.remove(arg)
            return path

    path = portable_dir()
    if path:
        return path

    logger.debug("Checking FS_UAE_BASE_DIR")
    path = os.environ.get("FS_UAE_BASE_DIR", "")
    if path:
        logger.debug("Base directory via FS_UAE_BASE_DIR: %s", repr(path))
        return path

    path = custom_path("base-dir")
    if path:
        logger.debug("Base directory via custom path config: %s", repr(path))
        return path

    path = os.path.join(documents_dir(True), "FS-UAE")
    if not os.path.exists(path):
        os.makedirs(path)
    # FIXME: normalize / case-normalize base dir?
    # path = Paths.get_real_case(path)
    logger.debug("Using default base dir %s", repr(path))
    return path
