import gzip
import io
import lzma
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from io import BytesIO
from typing import List, Optional, Tuple, cast

from fsgamesys.files.types import ByteStream
from fspy.zipfile import ZipFile

# This list is also used by the filescanner to add to recognized file
# extensions.
archive_extensions = [".zip", ".rp9"]

comments_as_bytes = True

from lhafile import LhaFile

archive_extensions.append(".lha")

# try:
#     from fsbc.seven_zip_file import SevenZipFile
# except ImportError:
#     traceback.print_exc()
#     print("[ARCHIVE] SevenZipFile module import problem")
#     SevenZipFile = None
# else:
#     archive_extensions.append(".7z")

archive_extensions_gz = [".gz", ".adz", ".roz"]
archive_extensions.extend(archive_extensions_gz)

archive_extensions_xz = [".xz"]
archive_extensions.extend(archive_extensions_xz)


# FIXME: getinfo needs to work for everything (return dummy data if necessary)


@dataclass
class MemberInfo:
    filename: str
    file_size: Optional[int] = None
    comment: Optional[bytes] = None


class Handler(ABC):
    # TODO:
    @abstractmethod
    def exists(self, name: str) -> bool:
        pass

    def getinfo(self, name: str):
        # An inefficient default implementation...
        for info in self.infolist():
            if info.filename == name:
                return info
        raise KeyError(name)

    @abstractmethod
    def infolist(self) -> List[MemberInfo]:
        pass

    @abstractmethod
    def list_files(self, subPath: str) -> List[str]:
        pass

    @abstractmethod
    def open(self, name: str) -> ByteStream:
        pass

    def read(self, name: str):
        return self.open(name).read()


class ZipHandler(Handler):
    def __init__(self, path: str):
        self.path = path
        self.zip = ZipFile(self.path, "r")

    def exists(self, name: str):
        try:
            self.zip.getinfo(name)
        except KeyError:
            return False
        else:
            return True

    def getinfo(self, name: str):
        # Needs tests!!
        return self.zip.getinfo(name)

    def infolist(self) -> List[MemberInfo]:
        return [
            MemberInfo(
                filename=x.filename, file_size=x.file_size, comment=x.comment
            )
            for x in self.zip.infolist()
        ]

    def list_files(self, subPath: str) -> List[str]:
        if subPath:
            return []
        return self.zip.namelist()

    def open(self, name: str) -> ByteStream:
        return self.zip.open(name)


class SimpleHandler(Handler):
    def __init__(self, name: str):
        self.name = name

    def exists(self, name: str):
        return name == self.name

    def infolist(self) -> List[MemberInfo]:
        return [MemberInfo(filename=self.name)]

    def list_files(self, subPath: str) -> List[str]:
        return [self.name]


class GzipHandler(SimpleHandler):
    def __init__(self, path: str):
        self.path = path
        name, ext = os.path.splitext(os.path.basename(path))
        ext = ext.lower()
        if ext == ".gz":
            # self.name = name
            pass
        elif ext == ".adz":
            name = name + ".adf"
        elif ext == ".roz":
            name = name + ".rom"
        else:
            raise Exception(
                "Unexpected extension {} in GzipHandler".format(ext)
            )
        super().__init__(name)

    def open(self, name: str) -> ByteStream:
        if name != self.name:
            raise LookupError("File not found")
        # read(n: int = -1) vs read(size: Optional[int])
        return cast(ByteStream, gzip.open(self.path, "rb"))


class XzHandler(SimpleHandler):
    def __init__(self, path: str):
        self.path = path
        name, ext = os.path.splitext(os.path.basename(path))
        ext = ext.lower()
        if ext == ".xz":
            pass
        else:
            raise Exception("Unexpected extension {} in XzHandler".format(ext))
        super().__init__(name)

    def open(self, name: str) -> ByteStream:
        if name != self.name:
            raise Exception("File not found")
        # read(n: int = -1) vs read(size: Optional[int])
        return cast(ByteStream, lzma.open(self.path, "rb"))


# class SevenZipHandler(object):
#     def __init__(self, path):
#         self.path = path
#         self.zip = SevenZipFile(self.path, "r")

#     def exists(self, name):
#         try:
#             self.zip.getinfo(name)
#         except KeyError:
#             return False
#         else:
#             return True

#     # FIXME: infolist

#     def list_files(self, sub_path):
#         if sub_path:
#             return
#         return self.zip.namelist()

#     def open(self, name):
#         data = self.zip.read(name)
#         return io.BytesIO(data)

#     def read(self, name):
#         return self.zip.read(name)


class LhaHandler(Handler):
    def __init__(self, path: str):
        self.path = path
        self._lhafile = LhaFile(self.path, "r")

    def decode_name(self, name: str):
        # FIXME: a little hack here, LhaFile uses os.sep
        # as path separator, normalizing to /
        name = name.replace(os.sep, "/")

        name = name.replace("%", "%25")
        name = name.replace("\\", "%5c")
        name = name.replace("/", os.sep)
        return name

    def encode_name(self, name: str) -> str:
        name = name.replace("\\", "/")
        name = name.replace("%5c", "\\")
        name = name.replace("%25", "%")
        # FIXME: a little hack here, LhaFile uses os.sep
        # as path separator
        name = name.replace("/", os.sep)
        return name

    def exists(self, name: str):
        # FIXME: Maybe look up in NameToInfo instead for quicker lookups
        name = self.encode_name(name)
        items = self._lhafile.infolist()
        for item in items:
            if item.filename == name:
                return True
        return False

    def _formatinfo(self, info):
        comment = info.comment
        if comments_as_bytes and isinstance(comment, str):
            # It might have been a mistake for LhaFile to decode the comment
            # as ISO-8859-1. We encode back and keep it as bytes, for
            # consistency with the ZipFile module... maybe. Alternatively,
            # decode zipfile comments as ISO-8859-1 instead...
            comment = comment.encode("ISO-8859-1")
        return MemberInfo(
            filename=info.filename,
            file_size=info.file_size,
            comment=comment,
        )

    def getinfo(self, name: str):
        # FIXME: Should instead add getinfo to LhaFile...
        info = self._lhafile.NameToInfo[self.encode_name(name)]
        return self._formatinfo(info)

    def infolist(self) -> List[MemberInfo]:
        result: List[MemberInfo] = []
        for info in self._lhafile.infolist():
            result.append(self._formatinfo(info))
        return result

    def list_files(self, subPath: str) -> List[str]:
        if subPath:
            return []
        result = []
        for name in self._lhafile.namelist():
            # if name.endswith("/"):
            #     continue
            result.append(self.decode_name(name))
        return result

    def open(self, name) -> ByteStream:
        # LhaFile does not have open method
        data = self._lhafile.read(self.encode_name(name))
        return io.BytesIO(data)


class NullHandler(Handler):
    def __init__(self, path: str):
        self.path = path

    def exists(self, name: str):
        return False

    def infolist(self) -> List[MemberInfo]:
        return []

    def list_files(self, subPath: str) -> List[str]:
        return []

    def open(self, name: str) -> ByteStream:
        return filter_open(name)


def filter_open(path: str, stream: Optional[ByteStream] = None) -> ByteStream:
    if stream is None:
        stream = open(path.rsplit("#?", 1)[0], "rb")
    if "#?" in path:
        # FIXME: Is there a nicer way to do this than doing these ugly
        # casts?
        if path.endswith("#?Filter=Skip(16)"):
            return SkipFilter(stream, 16)
        elif path.endswith("#?Filter=Skip(128)"):
            return SkipFilter(stream, 128)
        elif path.endswith("#?Filter=Skip(512)"):
            return SkipFilter(stream, 512)
        elif path.endswith("#?Filter=ByteSwapWords"):
            return ByteSwapWordsFilter(stream)
        else:
            raise Exception(
                "Unrecognized file filter: " + path.split("#?")[-1]
            )
    return stream


from typing_extensions import Protocol


class SupportsClose(Protocol):
    def close(self) -> None:
        ...


class SkipFilter:
    def __init__(self, stream: ByteStream, count: int):
        print("[ARCHIVE] Skip({}) filter for".format(count), stream)
        self.stream = stream
        self.count = count
        self.strip_left = count

    def read(self, n: int = -1) -> bytes:
        if self.strip_left:
            data = self.stream.read(self.strip_left)
            if len(data) == 0:
                # No data returned, end of stream
                return b""
            self.strip_left -= len(data)
        return self.stream.read(n)

    def close(self):
        self.stream.close()


class ByteSwapWordsFilter:
    def __init__(self, stream: ByteStream):
        print("[ARCHIVE] ByteSwapWords filter for", stream)
        self.stream = stream

    def read(self, n: int = -1):
        data = self.stream.read(n)
        # FIXME: Support odd length reads
        assert len(data) % 2 == 0
        io = BytesIO()
        for i in range(0, len(data), 2):
            io.write(data[i + 1 : i + 2])
            io.write(data[i : i + 1])
        io.seek(0)
        return io.getvalue()

    def close(self):
        self.stream.close()


class Archive(object):
    extensions = archive_extensions

    def __init__(self, path: str):
        self.path, self.sub_path = self.split_path(path)
        self._handler: Optional[Handler] = None

    def join(self, base: str, *args: str) -> str:
        return os.path.join(base, *args)

    def dirname(self, path: str) -> str:
        return os.path.dirname(path)

    def split_path(self, path: str) -> Tuple[str, str]:
        print("[ARCHIVE] Split path", path)
        if "#/" in path:
            parts = path.rsplit("#/", 1)
            archive = parts[0]
            # if not archive[-1] in "/\\" and os.path.exists(archive):
            if os.path.isfile(archive):
                sub_path = parts[1] if len(parts) > 1 else ""
                return archive, sub_path

        parts = path.replace("\\", "/").split("/")
        for i, part in enumerate(parts):
            _, ext = os.path.splitext(part)
            ext = ext.lower()
            if ext in archive_extensions:
                # FIXME: should also check that it isn't a dir
                path = str(os.sep).join(parts[: i + 1])
                sub_path = str(os.sep).join(parts[i + 1 :])
                return path, sub_path
        return path, ""

    def get_handler(self) -> Handler:
        if self._handler is not None:
            return self._handler
        print("[ARCHIVE] get_handler", self.path)
        _, ext = os.path.splitext(self.path)
        ext = ext.lower()
        # if ext == ".7z" and SevenZipFile is not None:
        #     self._handler = SevenZipHandler(self.path)
        #     return self._handler
        if ext in archive_extensions_gz:
            self._handler = GzipHandler(self.path)
            return self._handler
        if ext in archive_extensions_xz:
            self._handler = XzHandler(self.path)
            return self._handler
        try:
            self._handler = ZipHandler(self.path)
        except Exception as e:
            if ext == ".zip":
                print("[ARCHIVE]", repr(e))
            try:
                self._handler = LhaHandler(self.path)
            except Exception as e:
                if ext == ".lha":
                    print("[ARCHIVE]", repr(e))
                self._handler = NullHandler(self.path)
        return self._handler

    def list_files(self) -> List[str]:
        result: List[str] = []
        print("[ARCHIVE]", self.get_handler())
        for item in self.get_handler().list_files(self.sub_path):
            # result.append(os.path.join(self.path, item))
            result.append(self.path + "#/" + item)
        return result

    def exists(self, path: str):
        path, sub_path = self.split_path(path)
        # print(path, self.path)
        assert path == self.path
        if not sub_path:
            if "#?" in path:
                path = path.rsplit("#?", 1)[0]
            return os.path.exists(path)
        if "#?" in sub_path:
            sub_path = sub_path.rsplit("#?", 1)[0]
        return self.get_handler().exists(sub_path)

    def getinfo(self, path: str):
        path, sub_path = self.split_path(path)
        # print(path, self.path)
        assert path == self.path
        # if not sub_path:
        #     if "#?" in path:
        #         path = path.rsplit("#?", 1)[0]
        #     return os.path.exists(path)
        if "#?" in sub_path:
            sub_path = sub_path.rsplit("#?", 1)[0]
        return self.get_handler().getinfo(sub_path)

    def infolist(self):
        return self.get_handler().infolist()

    def open(self, path: str) -> ByteStream:
        print("[Archive] Open", repr(path))
        archive_path = path
        path, sub_path = self.split_path(path)
        # print(path, self.path)
        assert path == self.path
        if not sub_path:
            stream = filter_open(path)
        else:
            if "#?" in sub_path:
                sub_path = sub_path.rsplit("#?", 1)[0]
            stream = filter_open(path, self.get_handler().open(sub_path))
        stream.archive_path = archive_path
        return stream

    def copy(self, path: str, dest: str):
        ifo = self.open(path)
        with open(dest, "wb") as ofo:
            while True:
                data = ifo.read(65536)
                if not data:
                    break
                ofo.write(data)
