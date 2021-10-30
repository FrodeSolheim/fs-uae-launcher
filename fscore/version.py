import re
from typing import Any, List, Tuple, Union


class Version:
    """
    >>> Version("1.26.1.16-fs") == Version("1.26.1.16-fs")
    True
    >>> Version("1.26.1.16-fs") < Version("1.26.1.16-fs")
    False
    >>> Version("1.26.1.16-fs") > Version("1.26.1.16-fs")
    False
    """

    def __init__(self, version_string: str) -> None:
        self.string = version_string
        v = splitVersionString(version_string)
        self.major = int(v[0])
        self.minor = int(v[1] or "0")
        self.revision = int(v[2] or "0")
        self.build = int(v[3] or "0")
        self.val = self.major * 10000 ** 3
        self.val += self.minor * 10000 ** 2
        self.val += self.revision * 10000 ** 1
        self.val += self.build * 10000 ** 0
        self.mod = v[4]
        self.release = -1 if v[5] is None else int(v[5])
        # print(
        #     {
        #         "major": self.major,
        #         "minor": self.minor,
        #         "revision": self.revision,
        #         "build": self.build,
        #         "val": self.val,
        #         "mod": self.mod,
        #         "release": self.release,
        #     }
        # )

    def cmp_value(self) -> Tuple[int, str, int]:
        mod_cmp = self.mod or "~~e"
        if not mod_cmp.startswith("~"):
            mod_cmp = "~~" + mod_cmp
        return self.val, mod_cmp, self.release

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Version):
            return self.cmp_value() == other.cmp_value()
        return self == Version(str(other))

    def __lt__(self, other: "Version") -> bool:
        return self.cmp_value() < other.cmp_value()

    def __le__(self, other: "Version") -> bool:
        return self.cmp_value() <= other.cmp_value()

    def __gt__(self, other: "Version") -> bool:
        return self.cmp_value() > other.cmp_value()

    def __ge__(self, other: "Version") -> bool:
        return self.cmp_value() >= other.cmp_value()

    def __str__(self) -> str:
        return self.string

    @staticmethod
    def compare(a: Union["Version", str], b: Union["Version", str]) -> int:
        """
        >>> Version.compare("1.0.0", "1.0.1")
        -1
        >>> Version.compare("2.0.0", "1.0.1")
        1
        >>> Version.compare("1.2.3u2", "1.2.3")
        1
        >>> Version.compare("1.2.3a2", "1.2.3")
        -1
        >>> Version.compare("2.0.0", "2.0.0beta3")
        1
        >>> Version.compare("2.0.1", "2.0.0~beta3")
        1
        >>> Version.compare("2.0.0", "2.0.0~beta3")
        1
        >>> Version.compare("2.5.30~dev", "2.5.30")
        -1
        >>> Version.compare("2.5.30~dev2", "2.5.30~dev1")
        1
        >>> Version.compare("2.6beta", "2.5.30~dev1")
        1
        >>> Version.compare("2.6beta", "2.6")
        -1
        >>> Version.compare("2.6beta", "2.6.0")
        -1
        >>> Version.compare("2.6beta", "2.6.1")
        -1
        >>> Version.compare("2.6.0beta1", "2.6.1")
        -1
        >>> Version.compare("5.9.1.1", "5.9.1dev")
        1
        >>> Version.compare("5.9.1.1", "5.9.2dev")
        -1
        >>> Version.compare("3.8.1qemu2.2.0", "3.9.1qemu2.2.0")
        -1
        >>> Version.compare("3.8.1qemu2.4.0", "3.8.1qemu2.2.0")
        1
        >>> Version.compare("1.22.2-1", "1.22.2")
        1
        >>> Version.compare("1.22.2-0", "1.22.2")
        1
        >>> Version.compare("3.3-0", "3.4")
        -1
        >>> Version.compare("3.3-0", "3.3-1")
        -1
        >>> Version.compare("3.3~fs0", "3.4")
        -1
        >>> Version.compare("3.3~fs0", "3.3~fs1")
        -1
        >>> Version.compare("1.22.2fs1", "1.22.2")
        1
        >>> Version.compare("1.22.2fs0", "1.22.2")
        1
        >>> Version.compare("1.26.1.16-fs", "1.26.1.16-fs")
        0
        """
        # >>> Version.compare("2.6.0beta1", "2.6.0beta1.1")
        # -1
        # >>> Version.compare("2.6.0beta2", "2.6.0beta1.1")
        # 1
        if not isinstance(a, Version):
            a = Version(str(a))
        # elif isinstance(a, str):
        #     a = Version(a)
        # else:
        #     raise TypeError("Not a valid version string or object")
        if not isinstance(b, Version):
            b = Version(str(b))
        # elif isinstance(b, str):
        #     b = Version(b)
        # else:
        #     raise TypeError("Not a valid version string or object")
        # cmp is gone in Python 3
        return (a > b) - (a < b)


def splitVersionString(versionString: str) -> List[str]:
    pattern = re.compile(
        "^([0-9]{1,4})(?:\\.([0-9]{1,4}))?"
        "(?:\\.([0-9]{1,4}))?(?:\\.([0-9]{1,4}))?"
        "([-~]?[a-z0-9\\.]*)?(?:[-_]([0-9]+))?$"
    )
    m = pattern.match(versionString)
    if m is None:
        raise ValueError(f"{[versionString]} is not a valid version number")
    return list(m.groups())


if __name__ == "__main__":
    import doctest

    doctest.testmod()
