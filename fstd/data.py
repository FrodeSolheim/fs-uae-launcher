# import os
# noinspection PyUnresolvedReferences
from typing import IO, Dict, Optional
from zipfile import ZipFile

_archive: Optional[ZipFile] = None
_archive_initialized = False
_temp: Dict[str, str] = {}


def app_name() -> str:
    pass


def archive() -> ZipFile:
    global _archive
    # , _archive_initialized
    if _archive is None:
        archive_name = app_name() + ".dat"
        _archive = ZipFile(archive_name, "r")
    return _archive


def reset() -> None:
    global _archive
    # , _archive_initialized
    _archive = None
    # _archive_initialized = False


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
        raise NotImplementedError("No working implementation")
        # s = stream(name)
        # fd, p = tempfile.mkstemp(suffix=name)
        # with fd:
        #     fd.write(s.read())
        # _temp[name] = p
        # return p

    # if p is None:
    #     raise LookupError(name)
    # return p


# def stream(name: str, mode: str="rb") -> BinaryIO:
def stream(name: str) -> IO[bytes]:
    # archive().read()
    return archive().open(name)
