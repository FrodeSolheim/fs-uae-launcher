import traceback
from functools import wraps
from warnings import warn
from typing import Any, Callable, List, Dict, TypeVar, cast

F = TypeVar("F", bound=Callable[..., Any])

deprecation_warnings = set()


def deprecated(function: F) -> F:
    @wraps(function)
    def wrapper(*args: List[Any], **kwargs: Dict[Any, Any]):
        warn(f"{function.__name__} is deprecated", DeprecationWarning)
        location = str(traceback.extract_stack()[-2])
        if not location in deprecation_warnings:
            print(f"{function.__name__} is deprecated", location)
            deprecation_warnings.add(location)
        return function(*args, **kwargs)

    return cast(F, wrapper)
