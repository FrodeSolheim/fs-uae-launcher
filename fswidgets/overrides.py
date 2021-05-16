# Moved to a separate module to avoid import cycle between Widget and
# decorators.py

# Todo: Maybe use https://pypi.org/project/overrides/

from typing import Any, Callable, TypeVar

F = TypeVar("F", bound=Callable[..., Any])


def overrides(function: F) -> F:
    return function
