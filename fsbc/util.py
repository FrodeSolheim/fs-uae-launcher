from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import re
import warnings
import functools
import six


def memoize(func):
    memoize_dict = {}

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            key = (args, frozenset(kwargs.items()))
        except TypeError:
            # cannot create key -- for instance, passing a list as an argument.
            # FIXME: Log warning here
            return func(*args, **kwargs)
        try:
            return memoize_dict[key]
        except KeyError:
            value = func(*args, **kwargs)
            try:
                memoize_dict[key] = value
            except TypeError:
                # not cacheable -- for instance, passing a list as an
                # argument.
                # FIXME: Log warning here
                # FIXME: will not happen here.. se above type error?
                pass
            return value
    return wrapper


class Version (object):

    def __init__(self, version_string):
        self.string = str(version_string)
        v = split_version(version_string)
        self.major = int(v[0])
        self.minor = int(v[1] or 0)
        self.revision = int(v[2] or 0)
        self.build = int(v[3] or 0)
        self.val = self.major * 10000 ** 3
        self.val += self.minor * 10000 ** 2
        self.val += self.revision * 10000 ** 1
        self.val += self.build * 10000 ** 0
        self.mod = v[4]
        self.release = None if v[5] is None else int(v[5])

    def cmp_value(self):
        return self.val, self.mod or "o", int(self.release or 0)

    def __lt__(self, other):
        return self.cmp_value() < other.cmp_value()

    def __str__(self):
        return self.string


def split_version(version_string):
    pattern = re.compile(
        "^([0-9]{1,4})(?:\.([0-9]{1,4}))?"
        "(?:\.([0-9]{1,4}))?(?:\.([0-9]{1,4}))?"
        "(~?[a-z][a-z0-9]*)?(?:_([0-9]+))?$")
    m = pattern.match(version_string)
    if m is None:
        raise ValueError(version_string + " is not a valid version number")
    return m.groups()


def compare_versions(a, b):
    """
    >>> compare_versions("1.0.0", "1.0.1")
    -1
    >>> compare_versions("2.0.0", "1.0.1")
    1
    # >>> compare_versions("2.0.0", "2.0.0~beta3")
    # 1
    >>> compare_versions("2.0.0", "2.0.0beta3")
    1
    """
    if isinstance(a, Version):
        pass
    elif isinstance(a, six.string_types):
        a = Version(a)
    else:
        raise TypeError("Not a valid version string or object")
    if isinstance(b, Version):
        pass
    elif isinstance(b, six.string_types):
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
