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


def chained_exception(new_e, org_e):
    new_e.__cause__ = org_e
    return new_e


if __name__ == "__main__":
    import doctest

    doctest.testmod()
