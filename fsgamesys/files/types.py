from abc import abstractmethod
from typing import Dict, Optional, Protocol

from fsgamesys.files.installablefile import InstallableFile

# import typing
# typing.Protocol = typing.Any
# try:
#     from typing import Protocol
# except ImportError:
#     from typing import Any as Protocol  # type: ignore

# class InstallableFiles(dict):  # type: Dict[str, InstallableFile]

#     pass

InstallableFiles = Dict[str, InstallableFile]


class ByteStream(Protocol):

    # @abstractmethod
    # def read(self, n: Optional[int] = -1) -> bytes:
    #     ...

    @abstractmethod
    def read(self, n: int = -1) -> bytes:
        ...

    @abstractmethod
    def close(self):
        ...
