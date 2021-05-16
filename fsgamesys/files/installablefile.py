import hashlib
from typing import Optional


class InstallableFile:
    def __init__(
        self,
        sha1: Optional[str],
        size: Optional[int] = None,
        optional: bool = False,
        data: Optional[bytes] = None,
    ):
        self.sha1 = sha1
        self.size = size
        self.optional = optional
        self.data = data

    def __getitem__(self, key: str):
        # FIXME: Can remove soon
        if key == "sha1":
            return self.sha1
        if key == "optional":
            return self.optional
        raise KeyError(key)

    @classmethod
    def fromDirectory(cls):
        return cls(sha1=None)

    @classmethod
    def fromData(cls, data: bytes):
        return cls(
            sha1=hashlib.sha1(data).hexdigest(), size=len(data), data=data
        )
