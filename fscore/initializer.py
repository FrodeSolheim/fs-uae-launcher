from functools import wraps
from typing import Any, Callable, TypeVar, cast

F = TypeVar("F", bound=Callable[..., Any])


def initializer(function: F) -> F:
    """Decorator to call the function only once.

    The function will not return anything, and if an exception happens during
    first (and only) execution, nothing will happen on subsequent calls.
    """
    once_data = {
        "has_run": False,
    }

    @wraps(function)
    # def wrapper(*args, **kwargs):
    def wrapper() -> None:
        if once_data["has_run"]:
            return
        # Set has_run to true before calling function. If the function throws
        # an exception, this will only happen for the initial call.
        once_data["has_run"] = True
        # func(*args, **kwargs)
        function()

    return cast(F, wrapper)
