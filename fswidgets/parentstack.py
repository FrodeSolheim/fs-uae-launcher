from types import TracebackType
from typing import List, Optional, Type

from fswidgets.widget import Widget


class ParentStack:
    stack: List[Widget] = []

    @classmethod
    def top(cls) -> Widget:
        return cls.stack[-1]

    @classmethod
    def push(cls, widget: Widget) -> Widget:
        cls.stack.append(widget)
        return widget

    @classmethod
    def pop(cls, widget: Optional[Widget] = None) -> Widget:
        """Pops the topmost widget off the stack.

        If the widget parameter is specified, the function checks that the
        popped widget is identical to the parameter."""
        if widget:
            assert cls.top() == widget
        return cls.stack.pop()


class Parent:
    def __init__(self, parent: Widget):
        self.parent = parent

    def __enter__(self):
        ParentStack.push(self.parent)

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> bool:
        assert ParentStack.stack.pop() == self.parent
        return False


class AsParent:
    def __init__(self, parent: Widget):
        self.parent = parent

    def __enter__(self):
        ParentStack.push(self.parent)

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> bool:
        assert ParentStack.stack.pop() == self.parent
        return False
