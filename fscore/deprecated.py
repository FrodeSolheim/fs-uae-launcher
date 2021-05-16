import traceback
from functools import wraps
from typing import Any, Callable, Dict, List, Set, TypeVar, cast
from warnings import warn

# F = TypeVar("F", bound=Callable[..., Any])
# F = TypeVar("F", bound=Callable[None])

deprecation_warnings: Set[str] = set()


DeprecatedFunction = Callable[
    [
        Any,
        str,
        int,
        str,
        int,
        str,
        int,
        str,
        int,
        str,
        int,
        str,
        int,
    ],
    None,
]


def deprecated(function: Any) -> DeprecatedFunction:
    """The return signature is invalid on purpose, to mark errors when used."""

    # FIXME: Check option
    if False:

        @wraps(function)
        def wrapper(*args: List[Any], **kwargs: Dict[Any, Any]):
            warn(f"{function.__name__} is deprecated", DeprecationWarning)
            location = str(traceback.extract_stack()[-2])
            if not location in deprecation_warnings:
                print(f"{function.__name__} is deprecated", location)
                deprecation_warnings.add(location)
            return function(*args, **kwargs)

        # return cast(Deprecated, wrapper)
        return cast(DeprecatedFunction, wrapper)
        # return wrapper
    else:
        # Return function unmodified for best performance, but cast type to
        # let the static type analyzers flag usage.
        return cast(DeprecatedFunction, function)
