import os
import ctypes
import getpass
import subprocess
from fsbc.path import unicode_path
from fsbc.system import windows, macosx
from fsbc.util import memoize


if windows:
    from ctypes import windll, wintypes
    _SHGetFolderPath = windll.shell32.SHGetFolderPathW
    _SHGetFolderPath.argtypes = [
        wintypes.HWND, ctypes.c_int, wintypes.HANDLE, wintypes.DWORD,
        wintypes.LPCWSTR]

    def _err_unless_zero(result):
        if result == 0:
            return result
        else:
            raise WinPathsException(
                "Failed to retrieve windows path: %s" % result)

    _SHGetFolderPath.restype = _err_unless_zero

    S_OK = 0
    CSIDL_DESKTOP = 0
    CSIDL_PERSONAL = 5
    CSIDL_APPDATA = 26
    CSIDL_MYPICTURES = 39
    CSIDL_PROFILE = 40
    CSIDL_COMMON_DOCUMENTS = 46


@memoize
def get_user_name():
    user_name = getpass.getuser()
    return user_name


@memoize
def xdg_user_dir(name):
    if windows or macosx:
        return
    try:
        process = subprocess.Popen(["xdg-user-dir", name],
                                   stdout=subprocess.PIPE)
        path = process.stdout.read().strip()
        path = path.decode("UTF-8")
        print("XDG user dir {0} => {1}".format(name, repr(path)))
    except Exception:
        path = None
    return path


class WinPathsException(Exception):
    pass


# _get_path_buf from winpaths.py
def _get_path_buf(csidl):
    path_buf = ctypes.create_unicode_buffer(wintypes.MAX_PATH)
    result = _SHGetFolderPath(0, csidl, 0, 0, path_buf)
    if result != S_OK:
        raise RuntimeError(
            "Could not find common directory for CSIDL {}".format(csidl))
    return path_buf.value


@memoize
def get_desktop_dir(allow_create=True):
    if windows:
        path = _get_path_buf(CSIDL_DESKTOP)
    else:
        path = xdg_user_dir("DESKTOP")
        if not path:
            path = os.path.join(get_home_dir(), 'Desktop')
    path = unicode_path(path)
    if allow_create and not os.path.isdir(path):
        os.makedirs(path)
    return path


@memoize
def get_documents_dir(create=False):
    if windows:
        path = _get_path_buf(CSIDL_PERSONAL)
    elif macosx:
        path = os.path.join(get_home_dir(), 'Documents')
    else:
        path = xdg_user_dir("DOCUMENTS")
        if not path:
            path = get_home_dir()
    path = unicode_path(path)
    if create and not os.path.isdir(path):
        os.makedirs(path)
    return path


@memoize
def get_common_documents_dir():
    if windows:
        path = _get_path_buf(CSIDL_COMMON_DOCUMENTS)
    else:
        raise NotImplementedError("Only for windows")
    path = unicode_path(path)
    return path


@memoize
def get_pictures_dir(allow_create=True):
    if windows:
        path = _get_path_buf(CSIDL_MYPICTURES)
    else:
        path = xdg_user_dir("PICTURES")
        if not path:
            path = os.path.join(get_home_dir(), 'Pictures')
    path = unicode_path(path)
    if allow_create and not os.path.isdir(path):
        os.makedirs(path)
    return path


@memoize
def get_home_dir():
    if windows:
        path = _get_path_buf(CSIDL_PROFILE)
    else:
        path = os.path.expanduser("~")
    path = unicode_path(path)
    return path


@memoize
def get_data_dir(allow_create=True):
    if windows:
        path = _get_path_buf(CSIDL_APPDATA)
    elif macosx:
        path = os.path.join(get_home_dir(), "Library", "Application Support")
    else:
        path = os.path.join(get_home_dir(), ".local", "share")
        path = os.environ.get("XDG_DATA_HOME", path)
    path = unicode_path(path)
    if allow_create and not os.path.exists(path):
        os.makedirs(path)
    return path
