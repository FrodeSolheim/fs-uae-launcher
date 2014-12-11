from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import os
import sys
import six


def unicode_path(path):
    if isinstance(path, six.text_type):
        return path
    return path.decode(sys.getfilesystemencoding())


def str_path(path):
    if six.PY3:
        return path
    if isinstance(path, str):
        return path
    return path.encode(sys.getfilesystemencoding())


def normalize_path(path):
    path = os.path.normcase(os.path.normpath(path))
    return unicode_path(path)


def is_same_file(path_a, path_b):
    """Checks whether path_a and path_b refer to the same file. It does this
    by normalizing the paths (and case if applicable) and eliminating any
    symbolic links along the way."""
    path_a = normalize_path(os.path.realpath(path_a))
    path_b = normalize_path(os.path.realpath(path_b))
    return path_a == path_b
