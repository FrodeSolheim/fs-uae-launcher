import sys


def vendorDataclasses() -> None:
    try:
        import dataclasses  # type: ignore
    except ImportError:
        print("Could not find 'dataclasses', using vendored", file=sys.stderr)
        from _vendor import dataclasses  # type: ignore

        sys.modules["dataclasses"] = dataclasses


def vendorTypingExtensions() -> None:
    try:
        import typing_extensions  # type: ignore
    except ImportError:
        print(
            "Could not find 'typing_extensions', using vendored",
            file=sys.stderr,
        )
        from _vendor import typing_extensions  # type: ignore

        sys.modules["typing_extensions"] = typing_extensions


def init():
    vendorDataclasses()
    vendorTypingExtensions()
