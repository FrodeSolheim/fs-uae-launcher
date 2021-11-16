from dataclasses import dataclass, field
from typing import Dict, Optional, Type, TypeVar

from typing_extensions import Protocol

from fsui.qt.toplevelwidget import TopLevelWidget
from fswidgets.widget import Widget


@dataclass
class ShellOpenArgs:
    arguments: Dict[str, str] = field(default_factory=dict)
    argumentString: str = ""
    openedFrom: Optional[TopLevelWidget] = None


class ShellObject(Protocol):
    # @staticmethod
    # def open(
    #     arguments: Optional[Dict[str, str]] = None,
    #     argumentString: Optional[str] = None,
    #     **kwargs: Any
    # ) -> None:
    #     ...

    @classmethod
    def open(cls, openedFrom: Optional[TopLevelWidget] = None) -> None:
        args = ShellOpenArgs(openedFrom=openedFrom)
        cls.shellOpen(args)

    @classmethod
    def openFrom(cls, openedFrom: Widget) -> None:
        openedFromWindow = openedFrom.getWindow()
        args = ShellOpenArgs(openedFrom=openedFromWindow)
        cls.shellOpen(args)

    @staticmethod
    def shellOpen(args: ShellOpenArgs) -> None:
        ...


T = TypeVar("T", bound=Type[ShellObject])


def shellObject(cls: T) -> T:
    # FIXME: mypy does not seem to understand __globals__ here
    try:
        cls.shellOpen.__globals__["WorkspaceObject"] = cls  # type: ignore
        cls.shellOpen.__globals__["ShellObject"] = cls  # type: ignore
    except AttributeError:
        cls.open.__globals__["WorkspaceObject"] = cls  # type: ignore
        cls.open.__globals__["ShellObject"] = cls  # type: ignore
    return cls
