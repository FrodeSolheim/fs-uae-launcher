class ConfigEvent:
    __slots__ = ("key", "value")

    def __init__(self, key, value):
        self.key = key
        self.value = value
