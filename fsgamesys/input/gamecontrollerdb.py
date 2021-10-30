# from fscore.initializer import initializer
import os
from logging import getLogger
from typing import IO, Dict, Optional, Tuple

from fscore.applicationdata import ApplicationData
from fscore.filesystem import openWritableTextFileAtomic
from fsgamesys.FSGSDirectories import FSGSDirectories
from fsgamesys.input.gamecontroller import GameControllerMapping

log = getLogger(__name__)


class GameControllerDB:
    def __init__(self) -> None:
        self.mappings: Dict[str, GameControllerMapping] = {}
        self._loaded = False
        self.load()

    def load(self, forceReload: bool = False) -> None:
        # FIXME: For performance reasons, perhaps better to just load the
        # strings into memory and skip actually parsing for when the mappings
        # are actually needed (with caching)!
        if self._loaded:
            if forceReload:
                log.debug("Force reloading all mappings")
            else:
                return
        self.mappings.clear()
        stream = ApplicationData.stream(
            "SDL_GameControllerDB/gamecontrollerdb.txt"
        )
        if stream is not None:
            self.loadFromStream(stream, "SDL_GameControllerDB")
        self._loaded = True

        for mappingStr, extra in self.loadUserMappings().values():
            log.debug("User mapping: %r (extra: %r)", mappingStr, extra)
            self.tryLoadMapping(mappingStr, "User", extra=extra)

    def tryLoadMapping(
        self, mappingStr: str, source: str, extra: str = ""
    ) -> None:
        try:
            mapping = self.parseMapping(mappingStr)
        except Exception:
            log.exception("Exception while parsing mapping")
        else:
            mapping.source = source
            mapping.extra = extra
            self.mappings[mapping.guid] = mapping

    def loadFromStream(self, stream: IO[bytes], source: str) -> None:
        for lineBytes in stream.readlines():
            try:
                line = lineBytes.decode("UTF-8").strip()
            except Exception:
                log.exception("Exception while parsing mapping")
            else:
                if line and not line.startswith("#"):
                    self.tryLoadMapping(line, source)

    def getMapping(self, deviceGuid: str) -> Optional[GameControllerMapping]:
        try:
            return self.mappings[deviceGuid]
        except KeyError:
            # FIXME: Or exception or None?
            # mapping = GameControllerMapping()
            # mapping.source = ""
            # return mapping
            return None

    def parseMapping(self, mappingStr: str) -> GameControllerMapping:
        mapping = GameControllerMapping.fromString(mappingStr)
        return mapping

    def getUserMappingsFilePath(self) -> str:
        path = os.path.join(FSGSDirectories.get_data_dir(), "Controllers.txt")
        return path

    def loadUserMappings(self) -> Dict[str, Tuple[str, str]]:
        mappings: Dict[str, Tuple[str, str]] = {}
        lastGuid: str = ""
        filePath = self.getUserMappingsFilePath()
        try:
            with open(filePath, "r", encoding="UTF-8") as f:
                lines = f.readlines()
        except IOError:
            pass
        else:
            for line in lines:
                line = line.strip()
                if len(line) > 32 and line[32] == ",":
                    guid = line.split(",", 1)[0].lower()
                    mappings[guid] = (line.strip(), "")
                    lastGuid = guid
                elif (
                    line.startswith("#^")
                    and len(line) > 34
                    and line[34] == ","
                ):
                    guid = line[2:34].lower()
                    extra = line[35:].strip()
                    if guid == lastGuid:
                        mappings[guid] = (mappings[guid][0], extra)
        return mappings

    def saveUserMappings(self, mappings: Dict[str, Tuple[str, str]]) -> None:
        filePath = self.getUserMappingsFilePath()
        with openWritableTextFileAtomic(filePath) as f:
            for guid in sorted(mappings.keys()):
                mapping, extra = mappings[guid]
                f.write(f"{mapping}\r\n")
                if extra:
                    f.write(f"#^{guid},{extra}\r\n")
                f.write("\r\n")

    def saveUserMapping(self, mapping: GameControllerMapping) -> None:
        deviceGuid = mapping.guid.lower()
        log.debug("saveUserMapping for %r", deviceGuid)
        mappings = self.loadUserMappings()
        mappings[deviceGuid] = (mapping.toString(), mapping.extra)
        self.saveUserMappings(mappings)
        # Also replace mapping entry in global list of mappings.
        self.mappings[deviceGuid] = mapping.copy()

    def deleteUserMapping(self, deviceGuid: str) -> None:
        deviceGuid = deviceGuid.lower()
        log.debug("deleteUserMapping for %r", deviceGuid)
        mappings = self.loadUserMappings()
        try:
            del mappings[deviceGuid]
        except KeyError:
            log.debug(
                "Tried to delete user mapping for %r, but no such mapping was "
                "found",
                deviceGuid,
            )
        else:
            self.saveUserMappings(mappings)

        self.load(forceReload=True)


_instance: Optional[GameControllerDB] = None


def useGameControllerDB() -> GameControllerDB:
    global _instance
    if _instance is None:
        _instance = GameControllerDB()
    return _instance
