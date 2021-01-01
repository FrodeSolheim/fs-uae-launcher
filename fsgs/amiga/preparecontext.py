from typing import Optional, List
from fsgs.amiga.types import ConfigType, FilesType


class PrepareContext:
    def __init__(
        self,
        *,
        config: Optional[ConfigType] = None,
        files: Optional[FilesType] = None,
        args: Optional[List[str]] = None
    ):
        self.config: ConfigType = config or {}
        self.files: FilesType = files or {}
        self.args: List[str] = args or []
