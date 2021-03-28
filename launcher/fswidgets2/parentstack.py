from typing import List, Union

from fsui import Widget


class ParentStack:
    stack = []  # type: List[Union[Widget]]

    @classmethod
    def top(cls):
        return cls.stack[-1]

    @classmethod
    def push(cls, obj):
        cls.stack.append(obj)
        return obj

    @classmethod
    def pop(cls, obj=None):
        if obj:
            assert cls.top() == obj
        return cls.stack.pop()


class Parent:
    def __init__(self, parent):
        self.parent = parent

    def __enter__(self):
        ParentStack.push(self.parent)

    def __exit__(self, exception_type, exception_value, exception_traceback):
        assert ParentStack.stack.pop() == self.parent


class AsParent:
    def __init__(self, parent):
        self.parent = parent

    def __enter__(self):
        ParentStack.push(self.parent)

    def __exit__(self, exception_type, exception_value, exception_traceback):
        assert ParentStack.stack.pop() == self.parent
