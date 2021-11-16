from fsgamesys.FSGameSystemContext import FSGameSystemContext

fsgs = FSGameSystemContext()


def default_context() -> FSGameSystemContext:
    return fsgs


__all__ = ["default_context", "fsgs", "FSGameSystemContext"]
