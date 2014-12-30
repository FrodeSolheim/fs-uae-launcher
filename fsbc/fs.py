import os
import sys
import functools

# noinspection PyUnresolvedReferences
from fsbc.system import windows, macosx
# noinspection PyUnresolvedReferences
from fsbc.user import get_data_dir
# noinspection PyUnresolvedReferences
from .util import memoize


def cache(func):
    first_time = [True, None]

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if first_time[0]:
            first_time[1] = func(*args, **kwargs)
            first_time[0] = False
        return first_time[1]

    return wrapper


@cache
def get_lib_dir():
    lib_dir = os.environ.get('LIB_DIR', '').decode('UTF-8')
    if lib_dir:
        return unicode_path(lib_dir)
    lib_dir = os.path.join(os.getcwdu(), "lib")
    if os.path.exists(lib_dir):
        return lib_dir
    # raise RuntimeError("could not detect lib dir")
    return ""


EXCEPTION = "EXCEPTION"


@cache
def get_app_id():
    # FIXME
    return "fs-uae"
    # if windows or macosx:
    #     return "fs-uae"
    # else:
    #     return "fs-game-center"


@memoize
def get_app_data_dir(app=None):
    if not app:
        app = get_app_id()
    path = os.path.join(get_data_dir(), app)
    if not os.path.exists(path):
        os.makedirs(path)
    return path


@memoize
def get_app_config_dir(app=None):
    if not app:
        app = get_app_id()
    if windows:
        path = os.path.join(get_app_data_dir())
    elif macosx:
        path = os.path.join(get_home_dir(), "Library", "Preferences", app)
    else:
        path = os.path.join(get_home_dir(), ".config")
        path = os.environ.get('XDG_CONFIG_HOME', path)
        path = os.path.join(path, app)
        path = unicode_path(path)
    if not os.path.isdir(path):
        os.makedirs(path)
    return path


def cause(exc, _cause):
    exc.__cause__ = _cause
    _cause.__traceback__ = sys.exc_info()[2]
    return exc


def encode_path(path):
    return path


def unicode_path(path):
    return path


def from_utf8_str(obj):
    if isinstance(obj, bytes):
        return obj.decode("UTF-8")
    return str(obj)


def to_utf8_str(obj):
    return obj


def utf8(obj):
    return unicode_safe(obj, 'utf-8').encode('utf-8')


def utf8_safe(obj):
    return unicode_safe(obj, 'utf-8').encode('utf-8')


def unicode_safe(obj, encoding="ASCII"):
    try:
        return str(obj)
    except Exception:
        pass
    try:
        return str(obj, encoding, 'replace')
    except Exception:
        pass
    try:
        return str(str(obj), encoding, 'replace')
    except Exception:
        # logger.exception("Error in unicode_safe")
        return "String returned from unicode_safe (problem logged)"


def normalize_path(path):
    path = os.path.normcase(os.path.normpath(path))
    return unicode_path(path)


# noinspection PyUnresolvedReferences
from .user import get_home_dir
# noinspection PyUnresolvedReferences
from .util import Version
# noinspection PyUnresolvedReferences
from .util import split_version
# noinspection PyUnresolvedReferences
from .util import compare_versions
