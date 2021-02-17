from functools import wraps
from typing import Any, Callable, Dict, List, TypeVar, cast

F = TypeVar("F", bound=Callable[..., Any])


def memoize(function: F) -> F:
    memoize_data = {}

    @wraps(function)
    def wrapper(*args, **kwargs):
        try:
            key = (args, frozenset(kwargs.items()))
        except TypeError:
            # cannot create key -- for instance, passing a list as an argument.
            # FIXME: Log warning here
            return function(*args, **kwargs)
        try:
            return memoize_data[key]
        except KeyError:
            value = function(*args, **kwargs)
            try:
                memoize_data[key] = value
            except TypeError:
                # not cacheable -- for instance, passing a list as an
                # argument.
                # FIXME: Log warning here
                # FIXME: will not happen here.. se above type error?
                pass
            return value

    return cast(F, wrapper)
