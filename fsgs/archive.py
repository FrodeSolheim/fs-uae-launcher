import os
import io
import traceback

from io import BytesIO

from fsbc.zipfile import ZipFile

archive_extensions = [".zip", ".rp9"]

try:
    from lhafile import LhaFile
except ImportError:
    traceback.print_exc()
    print("[ARCHIVE] LhaFile module import problem")
    LhaFile = None
else:
    archive_extensions.append(".lha")

try:
    from fsbc.seven_zip_file import SevenZipFile
except ImportError:
    traceback.print_exc()
    print("[ARCHIVE] SevenZipFile module import problem")
    SevenZipFile = None
else:
    archive_extensions.append(".7z")


class ZipHandler(object):

    def __init__(self, path):
        self.path = path
        self.zip = ZipFile(self.path, "r")

    def list_files(self, sub_path):
        if sub_path:
            return
        return self.zip.namelist()
        # for name in self.zip.namelist():
        #     #if name.endswith(str("/")):
        #     #if name.endswith("/"):
        #     #    continue
        #     #yield self.decode_name(name)
        #     yield name

    def open(self, name):
        return self.zip.open(name)

    def exists(self, name):
        try:
            self.zip.getinfo(name)
        except KeyError:
            return False
        else:
            return True

    # def encode_name(self, name):
    #     name = name.replace("\\", "/")
    #     name = name.replace("%5f", "\\")
    #     name = name.replace("%25", "%")
    #     #name = name.encode("CP437")
    #     name = name.encode("ISO-8859-1")
    #     return name
    #
    # def decode_name(self, name):
    #     #name = name.decode("CP437")
    #     name = name.decode("ISO-8859-1")
    #     name = name.replace("%", "%25")
    #     name = name.replace("\\", "%5f")
    #     name = name.replace("/", os.sep)
    #     return name


class SevenZipHandler(object):

    def __init__(self, path):
        self.path = path
        self.zip = SevenZipFile(self.path, "r")

    def list_files(self, sub_path):
        if sub_path:
            return
        return self.zip.namelist()

    def read(self, name):
        return self.zip.read(name)

    def open(self, name):
        data = self.zip.read(name)
        return io.BytesIO(data)

    def exists(self, name):
        try:
            self.zip.getinfo(name)
        except KeyError:
            return False
        else:
            return True


class LhaHandler(object):

    def __init__(self, path):
        self.path = path
        self.zip = LhaFile(self.path, "r")

    def list_files(self, sub_path):
        if sub_path:
            return
        for name in self.zip.namelist():
            # if name.endswith(str("/")):
            #     continue
            yield self.decode_name(name)

    def open(self, name):
        name = self.encode_name(name)
        # LhaFile does not have open method
        data = self.zip.read(name)
        return io.BytesIO(data)

    def exists(self, name):
        name = self.encode_name(name)
        items = self.zip.infolist()
        for item in items:
            if item.filename == name:
                return True
        return False

        # try:
        #     self.zip.getinfo(name)
        # except KeyError:
        #     return False
        # else:
        #     return True

    def encode_name(self, name):
        name = name.replace("\\", "/")
        name = name.replace("%5f", "\\")
        name = name.replace("%25", "%")

        # FIXME: a little hack here, LhaFile uses os.sep
        # as path separator
        name = name.replace("/", os.sep)

        # name = name.encode("ISO-8859-1")
        return name

    def decode_name(self, name):
        # print("decode_name", name)

        # name = name.decode("ISO-8859-1")
        # FIXME: a little hack here, LhaFile uses os.sep
        # as path separator, normalizing to /
        name = name.replace(os.sep, "/")

        name = name.replace("%", "%25")
        name = name.replace("\\", "%5f")
        name = name.replace("/", os.sep)
        return name


class NullHandler(object):

    def __init__(self, path):
        self.path = path

    def list_files(self, _):
        return []

    def open(self, path):
        return filter_open(path)


def filter_open(path, stream=None):
    if stream is None:
        stream = open(path.rsplit("#?", 1)[0], "rb")
    if "#?" in path:
        if path.endswith("#?Filter=Skip(16)"):
            return SkipFilter(stream, 16)
        elif path.endswith("#?Filter=ByteSwapWords"):
            return ByteSwapWordsFilter(stream)
        else:
            raise Exception(
                "Unrecognized file filter: " + path.split("#?")[-1])
    return stream


class SkipFilter:
    def __init__(self, stream, count):
        print("[ARCHIVE] Skip({}) filter for".format(count), stream)
        self.stream = stream
        self.count = count
        self.strip_left = count

    def read(self, n=-1):
        if self.strip_left:
            data = self.stream.read(self.strip_left)
            if len(data) == 0:
                # No data returned, end of stream
                return b""
            self.strip_left -= len(data)
        return self.stream.read(n)


class ByteSwapWordsFilter:
    def __init__(self, stream):
        print("[ARCHIVE] ByteSwapWords filter for", stream)
        self.stream = stream

    def read(self, n=-1):
        data = self.stream.read(n)
        # FIXME: Support odd length reads
        assert len(data) % 2 == 0
        io = BytesIO()
        for i in range(0, len(data), 2):
            io.write(data[i + 1:i + 2])
            io.write(data[i:i + 1])
        io.seek(0)
        return io.getvalue()


class Archive(object):

    extensions = archive_extensions

    def __init__(self, path):
        self.path, self.sub_path = self.split_path(path)
        self._handler = None

    def join(self, base, *args):
        return os.path.join(base, *args)

    def dirname(self, path):
        return os.path.dirname(path)

    def split_path(self, path):
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
            n, ext = os.path.splitext(part)
            ext = ext.lower()
            if ext in archive_extensions:
                # FIXME: should also check that it isn't a dir
                path = str(os.sep).join(parts[:i + 1])
                sub_path = str(os.sep).join(parts[i + 1:])
                return path, sub_path
        return path, ""

    def get_handler(self):
        if self._handler is not None:
            return self._handler
        print("[ARCHIVE] get_handler", self.path)
        name, ext = os.path.splitext(self.path)
        ext = ext.lower()
        if ext == ".7z" and SevenZipFile is not None:
            self._handler = SevenZipHandler(self.path)
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

    def list_files(self):
        result = []
        print("[ARCHIVE]", self.get_handler())
        for item in self.get_handler().list_files(self.sub_path):
            # result.append(os.path.join(self.path, item))
            result.append(self.path + "#/" + item)
        return result

    def exists(self, path):
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

    def open(self, path):
        print("[Archive] Open", repr(path))
        path, sub_path = self.split_path(path)
        # print(path, self.path)
        assert path == self.path
        if not sub_path:
            return filter_open(path)
        if "#?" in sub_path:
            sub_path = sub_path.rsplit("#?", 1)[0]
        return filter_open(path, self.get_handler().open(sub_path))

    def copy(self, path, dest):
        ifo = self.open(path)
        with open(dest, "wb") as ofo:
            while True:
                data = ifo.read(65536)
                if not data:
                    break
                ofo.write(data)
