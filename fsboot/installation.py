from fsboot import is_portable


class Installation:
    @staticmethod
    def isPortable() -> bool:
        return is_portable()
