import re
from typing import Any, List, Union

# Moved to fspy.decorators


def unused(_: Any) -> None:
    pass


def is_sha1(value: str) -> bool:
    if len(value) != 40:
        return False
    for c in value:
        if c not in "0123456789abcdef":
            return False
    return True


def is_uuid(value: str) -> str:
    """
    >>> is_uuid("2c244488-4a91-4c21-a0b7-0f731d4336c7")
    '2c244488-4a91-4c21-a0b7-0f731d4336c7'
    >>> is_uuid("test")
    ''
    """
    match = re.match(
        "^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
        value.lower(),
    )
    if match is not None:
        return match.group(0)
    return ""


def split_version(version_string: str) -> List[str]:
    pattern = re.compile(
        "^([0-9]{1,4})(?:\.([0-9]{1,4}))?"
        "(?:\.([0-9]{1,4}))?(?:\.([0-9]{1,4}))?"
        "([-~]?[a-z0-9\.]*)?(?:[-_]([0-9]+))?$"
    )
    m = pattern.match(version_string)
    if m is None:
        raise ValueError(version_string + " is not a valid version number")
    return list(m.groups())


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
        v = split_version(version_string)
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

    def cmp_value(self):
        mod_cmp = self.mod or "~~e"
        if not mod_cmp.startswith("~"):
            mod_cmp = "~~" + mod_cmp
        return self.val, mod_cmp, self.release

    def __eq__(self, other) -> bool:
        return self.cmp_value() == other.cmp_value()

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


def compare_versions(a: Union[Version, str], b: Union[Version, str]):
    """
    >>> compare_versions("1.0.0", "1.0.1")
    -1
    >>> compare_versions("2.0.0", "1.0.1")
    1
    >>> compare_versions("1.2.3u2", "1.2.3")
    1
    >>> compare_versions("1.2.3a2", "1.2.3")
    -1
    >>> compare_versions("2.0.0", "2.0.0beta3")
    1
    >>> compare_versions("2.0.1", "2.0.0~beta3")
    1
    >>> compare_versions("2.0.0", "2.0.0~beta3")
    1
    >>> compare_versions("2.5.30~dev", "2.5.30")
    -1
    >>> compare_versions("2.5.30~dev2", "2.5.30~dev1")
    1
    >>> compare_versions("2.6beta", "2.5.30~dev1")
    1
    >>> compare_versions("2.6beta", "2.6")
    -1
    >>> compare_versions("2.6beta", "2.6.0")
    -1
    >>> compare_versions("2.6beta", "2.6.1")
    -1
    >>> compare_versions("2.6.0beta1", "2.6.1")
    -1
    >>> compare_versions("5.9.1.1", "5.9.1dev")
    1
    >>> compare_versions("5.9.1.1", "5.9.2dev")
    -1
    >>> compare_versions("3.8.1qemu2.2.0", "3.9.1qemu2.2.0")
    -1
    >>> compare_versions("3.8.1qemu2.4.0", "3.8.1qemu2.2.0")
    1
    >>> compare_versions("1.22.2-1", "1.22.2")
    1
    >>> compare_versions("1.22.2-0", "1.22.2")
    1
    >>> compare_versions("3.3-0", "3.4")
    -1
    >>> compare_versions("3.3-0", "3.3-1")
    -1
    >>> compare_versions("3.3~fs0", "3.4")
    -1
    >>> compare_versions("3.3~fs0", "3.3~fs1")
    -1
    >>> compare_versions("1.22.2fs1", "1.22.2")
    1
    >>> compare_versions("1.22.2fs0", "1.22.2")
    1
    >>> compare_versions("1.26.1.16-fs", "1.26.1.16-fs")
    0
    """
    # >>> compare_versions("2.6.0beta1", "2.6.0beta1.1")
    # -1
    # >>> compare_versions("2.6.0beta2", "2.6.0beta1.1")
    # 1
    if isinstance(a, Version):
        pass
    elif isinstance(a, str):
        a = Version(a)
    else:
        raise TypeError("Not a valid version string or object")
    if isinstance(b, Version):
        pass
    elif isinstance(b, str):
        b = Version(b)
    else:
        raise TypeError("Not a valid version string or object")
    # cmp is gone in Python 3
    return (a > b) - (a < b)


def chained_exception(new_e, org_e):
    new_e.__cause__ = org_e
    return new_e


if __name__ == "__main__":
    import doctest

    doctest.testmod()
