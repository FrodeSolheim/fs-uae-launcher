from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from fsbc.user import get_home_dir
from fsbc.util import memoize
from fsbc.Paths import Paths


def expand_path(path):
    return Paths.expand_path(path)


def get_real_case(path):
    return Paths.get_real_case(path)
