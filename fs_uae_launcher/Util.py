# noinspection PyUnresolvedReferences
from fsbc.user import get_home_dir
# noinspection PyUnresolvedReferences
from fsbc.util import memoize
from fsbc.Paths import Paths


def expand_path(path):
    return Paths.expand_path(path)


def get_real_case(path):
    return Paths.get_real_case(path)
