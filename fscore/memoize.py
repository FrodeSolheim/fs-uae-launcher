from functools import wraps
from typing import Any, Callable, Dict, TypeVar, cast

# FIXME: Using ParamSpec when supported in mypy *and* Visual Studio code
# from typing_extensions import ParamSpec
# T = TypeVar("T")
# P = ParamSpec("P")

F = TypeVar("F", bound=Callable[..., Any])


def memoize(function: F) -> F:
    # def memoize(function: Callable[P, T]) -> T:
    # memoize_data: Dict[Any, R] = {}
    memoize_data: Dict[Any, Any] = {}

    @wraps(function)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
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


# @memoize
# def double(a: int):
#     return a * 2

# b = double(2)

# @memoize
# def dosomething(a: int, b: str):
#     return str(a) + b

# c = dosomething(2, "hello")
