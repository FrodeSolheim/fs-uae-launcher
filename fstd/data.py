# import os
import tempfile
import zipfile

# noinspection PyUnresolvedReferences
from typing import BinaryIO, Dict

_archive = None  # type: zipfile.ZipFile
_archive_initialized = False
_temp = {}  # type: Dict[str, str]


def app_name() -> str:
    pass


def archive() -> zipfile.ZipFile:
    global _archive, _archive_initialized
    if _archive_initialized:
        return _archive
    archive_name = app_name() + ".dat"
    _archive = zipfile.ZipFile(archive_name, "r")
    return _archive


def reset() -> None:
    global _archive, _archive_initialized
    _archive = None
    _archive_initialized = False


def path_no_extract(name: str) -> str:
    return name


def path(name: str) -> str:
    try:
        return _temp[name]
    except KeyError:
        pass
    try:
        return path_no_extract(name)
    except LookupError:
        s = stream(name)
        fd, p = tempfile.mkstemp(suffix=name)
        with fd:
            fd.write(s.read())
        _temp[name] = p
        return p

    # if p is None:
    #     raise LookupError(name)
    # return p


# def stream(name: str, mode: str="rb") -> BinaryIO:
def stream(name: str) -> BinaryIO:
    # archive().read()
    return archive().open(name)
