import inspect
import logging
from typing import (
    Callable,
    ClassVar,
    Generic,
    List,
    Type,
    TypeVar,
    Union,
    cast,
)

from fscore.types import SimpleCallable

log = logging.getLogger(__name__)


class Event:
    type: ClassVar[str]

    # def __init__(self) -> None:
    #     pass


T = TypeVar("T", bound=Event)

EventListener = Union[Callable[[T], None], SimpleCallable]


class EventHelper(Generic[T]):
    def __init__(self, eventType: Type[T]) -> None:
        self.eventType = eventType
        self.listeners: List[EventListener[T]] = []

    # FIXME: Couldn't find a way to type this to work from addEventListener
    # def addListener(self, listener: Callable[[Any], None]) -> SimpleCallable:
    def addListener(self, listener: EventListener[T]) -> SimpleCallable:
        log.debug("Adding %r listener %r", self.eventType.type, listener)
        self.listeners.append(listener)

        def removeListener() -> None:
            self.removeListener(listener)

        return removeListener

    # FIXME: Couldn't find a way to type this to work from removeEventListener
    # def removeListener(self, listener: Callable[[Any], None]) -> None:
    def removeListener(self, listener: EventListener[T]) -> None:
        log.debug("Removing %r listener %r", self.eventType.type, listener)
        self.listeners.remove(listener)

    def emit(self, event: T) -> None:
        for listener in self.listeners:
            sig = inspect.signature(listener)
            if len(sig.parameters) == 0:
                # FIXME: Is there some kind of typing.restrict function which
                # works like cast but also checks that the type being casted
                # to is part of a union or a specialization of the type?
                cast(Callable[[], None], listener)()
            else:
                cast(Callable[[T], None], listener)(event)

    def __call__(self, event: T) -> None:
        # FIXME: Deprecated
        self.emit(event)
