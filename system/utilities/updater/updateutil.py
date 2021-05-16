import logging
import logging.config
import os
from configparser import ConfigParser
from typing import Optional

import fsboot

log = logging.getLogger(__name__)


class UpdateUtil:
    @staticmethod
    def getSystemDirectory() -> str:
        return os.path.join(fsboot.base_dir(), "System")

    @staticmethod
    def getPluginVersionFromDirectory(pluginDir: str) -> str:
        configParser = ConfigParser()
        configParser.read(os.path.join(pluginDir, "Plugin.ini"))
        return configParser.get("plugin", "version")

    @classmethod
    def getPluginDirectory(cls, pluginName: str):
        systemDir = cls.getSystemDirectory()
        return os.path.join(systemDir, pluginName)

    @classmethod
    def getPluginVersion(cls, pluginName: str) -> Optional[str]:
        configParser = ConfigParser()
        pluginDir = cls.getPluginDirectory(pluginName)
        pluginIni = os.path.join(pluginDir, "Plugin.ini")
        if not os.path.exists(pluginIni):
            return None
        configParser.read(pluginIni)
        return configParser.get("plugin", "version")
