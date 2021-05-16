import os
import sys
from typing import Union


def unicode_path(path: Union[bytes,str]):
    if isinstance(path, str):
        return path
    return path.decode(sys.getfilesystemencoding())


def str_path(path: str):
    return path


def normalize_path(path: str):
    path = os.path.normcase(os.path.normpath(path))
    return unicode_path(path)


def is_same_file(path_a: str, path_b: str):
    """Checks whether path_a and path_b refer to the same file. It does this
    by normalizing the paths (and case if applicable) and eliminating any
    symbolic links along the way."""
    path_a = normalize_path(os.path.realpath(path_a))
    path_b = normalize_path(os.path.realpath(path_b))
    return path_a == path_b
