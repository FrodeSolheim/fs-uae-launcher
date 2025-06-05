"""
The goals of this class are:
1. To be able to use ISO-8859-1 encoding instead of CP43, and
2. Also support zip files with UTF-8 encoding, and

Python 3 assumes strings must be converted to CP437 for non-ASCII characters.
This is why there'll be decoding/encoding from/to CP437 even for ISO-8859-1
and UTF-8 name lookup (with Python 3). Complications arise because Python
seems to detect UTF-8 in some zip files (based on a flag) and then
automatically convert to/from unicode.
"""

import os
import sys
import zipfile
import zlib

try:
    from typing import List
except ImportError:
    from fstd.typing import List


class ZipFile(zipfile.ZipFile):
    def __init__(self, path: str, mode: str = "r") -> None:
        zipfile.ZipFile.__init__(self, path, mode)

    def getinfo(self, name: str) -> zipfile.ZipInfo:
        try:
            n = name.encode("ISO-8859-1").decode("CP437")
            return zipfile.ZipFile.getinfo(self, n)
        except Exception:
            pass
        try:
            n = name.encode("UTF-8").decode("CP437")
            return zipfile.ZipFile.getinfo(self, n)
        except Exception:
            pass
        return zipfile.ZipFile.getinfo(self, name)

    def namelist(self) -> List[str]:
        names = zipfile.ZipFile.namelist(self)
        for i, name in enumerate(names):
            print("...", repr(name))
            try:
                name = name.encode("CP437").decode("UTF-8")
            except Exception:
                try:
                    name = name.encode("CP437").decode("ISO-8859-1")
                except Exception:
                    pass
            names[i] = name
        return names


def _get_compressor(compress_type):
    if compress_type == zipfile.ZIP_DEFLATED:
        return zlib.compressobj(9, zlib.DEFLATED, -15)
    # noinspection PyProtectedMember,PyUnresolvedReferences
    return zipfile._get_compressor_fspy(compress_type)


def create_deterministic_archive(
    src, dst, fix_pyc_timestamps=False, torrentzip=False
):
    sz = ZipFile(src, "r")
    # Sort and remove duplicates
    names = sorted(set(sz.namelist()), key=str.lower)
    # FIXME: Remove non-needed empty directories
    dz = ZipFile(dst, "w")
    for name in names:
        data = sz.read(name)
        if name.endswith(".pyc") and fix_pyc_timestamps:
            data = data[0:4] + b"\x00\x00\x00\x00" + data[8:]
        zinfo = zipfile.ZipInfo()
        zinfo.filename = name
        zinfo.date_time = (1996, 12, 24, 23, 32, 00)
        zinfo.compress_type = zipfile.ZIP_DEFLATED
        zinfo.create_system = 0
        zinfo.create_version = 0
        zinfo.extract_version = 20
        zinfo.flag_bits = 2
        if torrentzip:
            zinfo.external_attr = 0
        else:
            zinfo.external_attr = (0o644 & 0xFFFF) << 16
            if name.endswith("/"):
                # FIXME: Check if this is correct?
                zinfo.external_attr |= 0x10
        try:
            if torrentzip:
                # noinspection PyProtectedMember
                zipfile._get_compressor_fspy = zipfile._get_compressor
                zipfile._get_compressor = _get_compressor
            dz.writestr(zinfo, data)
        finally:
            if torrentzip:
                # noinspection PyProtectedMember,PyUnresolvedReferences
                zipfile._get_compressor = zipfile._get_compressor_fspy
                # noinspection PyProtectedMember,PyUnresolvedReferences
                del zipfile._get_compressor_fspy
    sz.close()
    if torrentzip:
        # Placeholder for the CRC-32 of the central directory records.
        dz.comment = b"TORRENTZIPPED-XXXXXXXX"
    dz.close()
    if torrentzip:
        with open(dst, "r+b") as f:
            f.seek(-22 - 2 - 4 - 4, 2)
            size = (
                f.read(1)[0]
                + f.read(1)[0] * 256
                + f.read(1)[0] * 256**2
                + f.read(1)[0] * 256**2
            )
            socd = (
                f.read(1)[0]
                + f.read(1)[0] * 256
                + f.read(1)[0] * 256**2
                + f.read(1)[0] * 256**2
            )
            f.seek(socd)
            data = f.read(size)
            checksum = zlib.crc32(data)
            f.seek(-8, 2)
            f.write("{:X}".format(checksum).encode("ASCII"))


def convert_deterministic_archive(
    src, fix_pyc_timestamps=False, torrentzip=False
):
    tmp = os.path.join(
        os.path.dirname(src), ".~" + os.path.basename(src) + ".tmp"
    )
    try:
        create_deterministic_archive(
            src,
            tmp,
            fix_pyc_timestamps=fix_pyc_timestamps,
            torrentzip=torrentzip,
        )
        os.remove(src)
        os.rename(tmp, src)
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)


def main():
    if len(sys.argv) > 1:
        if sys.argv[1] == "deterministic":
            fix_pyc_timestamps = False
            if "--fix-pyc-timestamps" in sys.argv:
                sys.argv.remove("--fix-pyc-timestamps")
                fix_pyc_timestamps = True
            torrentzip = False
            if "--torrentzip" in sys.argv:
                sys.argv.remove("--torrentzip")
                torrentzip = True
            if len(sys.argv) == 3:
                convert_deterministic_archive(
                    sys.argv[2],
                    torrentzip=torrentzip,
                    fix_pyc_timestamps=fix_pyc_timestamps,
                )
            else:
                create_deterministic_archive(
                    sys.argv[2],
                    sys.argv[3],
                    torrentzip=torrentzip,
                    fix_pyc_timestamps=fix_pyc_timestamps,
                )


if __name__ == "__main__":
    main()
