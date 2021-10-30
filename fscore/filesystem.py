# from fscore.initializer import initializer
import os
from contextlib import contextmanager
from logging import getLogger
from typing import IO, Iterator

log = getLogger(__name__)


def createTempNameForFile(filePath: str) -> str:
    return os.path.join(
        os.path.dirname(filePath), f".~{os.path.basename(filePath)}.tmp"
    )


# @overload
# @contextmanager
# def openWritableFileAtomic(filePath: str, mode: Literal["w"], encoding:str = "UTF-8") -> Iterator[IO[bytes]]:
#     ...
#
# @overload
# @contextmanager
# def openWritableFileAtomic(filePath: str, mode: Literal["wb"], encoding:str = "UTF-8") -> Iterator[IO[str]]:
#     ...


def _prepareWritableFileAtomic(filePath: str) -> str:
    dirPath = os.path.dirname(filePath)
    if not os.path.exists(dirPath):
        log.debug("Creating directory %r", dirPath)
        os.makedirs(dirPath)
    tempName = createTempNameForFile(filePath)
    log.debug("Opening temporary file %r for writing", tempName)
    return tempName


def _finalizeWritableFileAtomic(tempName: str, filePath: str) -> None:
    if os.path.exists(filePath):
        log.debug("Removing existing file %r", filePath)
        os.remove(filePath)
    log.debug("Renaming %r to %r", tempName, filePath)
    os.rename(tempName, filePath)


@contextmanager
def openWritableFileAtomic(filePath: str) -> Iterator[IO[bytes]]:
    """Also creates intermediate directories if needed."""
    tempName = _prepareWritableFileAtomic(filePath)
    f = open(tempName, "wb")
    try:
        yield f
    except Exception:
        raise
    else:
        f.close()
        _finalizeWritableFileAtomic(tempName, filePath)
    finally:
        f.close()


# Duplicate implementation because I didn't get the type hints correct for
# overloads on the mode parameter.
@contextmanager
def openWritableTextFileAtomic(
    filePath: str, encoding: str = "UTF-8"
) -> Iterator[IO[str]]:
    """Also creates intermediate directories if needed."""
    tempName = _prepareWritableFileAtomic(filePath)
    f = open(tempName, "w", encoding=encoding)
    try:
        yield f
    except Exception:
        raise
    else:
        f.close()
        _finalizeWritableFileAtomic(tempName, filePath)
    finally:
        if not f.closed:
            f.close()


# with openWritableFileAtomic("aaa") as f:
#     pass
# with openWritableTextFileAtomic("aaa") as g:
#     pass
