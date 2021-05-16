from typing import List, Optional

from fsgamesys.amiga.types import ConfigType
from fsgamesys.files.installablefiles import InstallableFiles


class PrepareContext:
    def __init__(
        self,
        *,
        config: Optional[ConfigType] = None,
        files: Optional[InstallableFiles] = None,
        args: Optional[List[str]] = None
    ):
        self.config: ConfigType = config or {}
        self.files: InstallableFiles = files or {}
        self.args: List[str] = args or []
