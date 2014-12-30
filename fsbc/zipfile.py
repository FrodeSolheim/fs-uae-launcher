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
import zipfile
from typing import List


class ZipFile(zipfile.ZipFile):

    def __init__(self, path: str, mode: str="r") -> None:
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
