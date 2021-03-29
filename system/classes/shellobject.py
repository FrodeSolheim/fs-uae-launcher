def shellObject(cls):
    cls.open.__globals__["WorkspaceObject"] = cls
    return cls
