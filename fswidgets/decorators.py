from functools import wraps
from typing import Any, Callable, Dict, List, TypeVar, cast

from fswidgets.parentstack import ParentStack
from fswidgets.widget import Widget

F = TypeVar("F", bound=Callable[..., Any])


def constructor(function: F) -> F:
    @wraps(function)
    def wrapper(self: Widget, *args: List[Any], **kwargs: Dict[Any, Any]):
        ParentStack.push(self)
        try:
            result = function(self, *args, **kwargs)
        finally:
            ParentStack.pop(self)
        return result

    return cast(F, wrapper)
