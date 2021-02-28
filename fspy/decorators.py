import traceback
from functools import wraps
from warnings import warn

deprecation_warnings = set()


def deprecated(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        warn(f"{function.__name__} is deprecated", DeprecationWarning)
        # FIXME: Temporarily disabled, due to error when running via frozen
        # (cx_Freeze) executable - error retrieving stack with error like:
        #   File "/usr/lib/python3.8/tokenize.py", line 371, in detect_encoding
        #     encoding = find_cookie(first)
        #   File "/usr/lib/python3.8/tokenize.py", line 335, in find_cookie
        #     raise SyntaxError(msg)
        #   File "<string>", line None
        # SyntaxError: invalid or missing encoding declaration for 'fs-uae-launcher'
        # location = str(traceback.extract_stack()[-2])
        # if not location in deprecation_warnings:
        #     print(f"{function.__name__} is deprecated", location)
        #     deprecation_warnings.add(location)
        return function(*args, **kwargs)

    return wrapper


def memoize(func):
    memoize_data = {}

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            key = (args, frozenset(kwargs.items()))
        except TypeError:
            # cannot create key -- for instance, passing a list as an argument.
            # FIXME: Log warning here
            return func(*args, **kwargs)
        try:
            return memoize_data[key]
        except KeyError:
            value = func(*args, **kwargs)
            try:
                memoize_data[key] = value
            except TypeError:
                # not cacheable -- for instance, passing a list as an
                # argument.
                # FIXME: Log warning here
                # FIXME: will not happen here.. se above type error?
                pass
            return value

    return wrapper


def initializer(func):
    """Decorator to call the function only once.

    The function will not return anything, and if an exception happens during
    first (and only) execution, nothing will happen on subsequent calls.
    """
    once_data = {
        "has_run": False,
    }

    @wraps(func)
    # def wrapper(*args, **kwargs):
    def wrapper():
        if once_data["has_run"]:
            return
        # Set has_run to true before calling function. If the function throws
        # an exception, this will only happen for the initial call.
        once_data["has_run"] = True
        # func(*args, **kwargs)
        func()

    return wrapper
