# from fscore.initializer import initializer
import os
from logging import getLogger
from typing import IO, Dict, List, Optional, Tuple

from fscore.applicationdata import ApplicationData
from fscore.filesystem import openWritableTextFileAtomic
from fsgamesys.FSGSDirectories import FSGSDirectories
from fsgamesys.input.gamecontroller import GameControllerMapping

log = getLogger(__name__)


class GameControllerDB:
    def __init__(self) -> None:
        self.database: Dict[str, Tuple[str, str, str]] = {}
        self.mappings: Dict[str, Optional[GameControllerMapping]] = {}
        self._loaded = False
        self.load()

    def getUserGameControllersDir(self) -> str:
        return os.path.join(FSGSDirectories.get_data_dir(), "GameControllerDB")

    # FIXME: Move to FSGSDirectories?
    def getUserMappingsFilePath(self) -> str:
        path = os.path.join(
            FSGSDirectories.get_data_dir(), "GameControllerDB", "99-User.txt"
        )
        return path

    def findConfigFiles(self) -> List[str]:
        files: Dict[str, List[str]] = {}
        for filePath in [
            "Data:GameControllerDB/25-SDL_GameControllerDB.txt",
            "Data:GameControllerDB/50-SDL2.txt",
            "Data:GameControllerDB/75-OpenRetro.txt",
        ]:
            _, fileName = filePath.rsplit("/", 1)
            files.setdefault(fileName, []).append(filePath)

        configDir = self.getUserGameControllersDir()
        if os.path.isdir(configDir):
            for fileName in os.listdir(configDir):
                if fileName.endswith(".txt"):
                    filePath = os.path.join(configDir, fileName)
                    files.setdefault(fileName, []).append(filePath)

        result: List[str] = []
        configFileNames = sorted(files.keys())
        if "99-User.txt" in configFileNames:
            configFileNames.remove("99-User.txt")
            # Loading via self.loadUserMappings() instead, at least for now.
            # configFileNames.append("99-User.txt")
        for configFileName in configFileNames:
            candidates = files[configFileName]
            # Use last entry for now. Might implemented smarter sorting later.
            result.append(candidates[-1])
        return result

    def load(self, forceReload: bool = False) -> None:
        # For performance reasons, we load the mappings string into memory and
        # skip actually parsing for when the mappings until needed (cached).
        if self._loaded:
            if forceReload:
                log.debug("Force reloading all mappings")
            else:
                return
        self.database.clear()
        self.mappings.clear()

        # Load user mapping first. Mappings loaded first "wins" on conflict.
        for guid, (mappingString, extra) in self.loadUserMappings().items():
            log.debug("User mapping: %r (extra: %r)", mappingString, extra)
            # self.tryLoadMapping(mappingStr, "User", extra=extra)
            self.database[guid] = (mappingString, "99-User.txt", extra)

        # Then we load the rest of the database.
        configFiles = self.findConfigFiles()
        log.debug("Controller config files: %r", configFiles)
        for configFile in reversed(configFiles):
            if configFile.startswith("Data:"):
                stream = ApplicationData.stream(configFile[len("Data:") :])
                # if stream is not None:
                # self.loadFromStream(stream, "SDL_GameControllerDB")
                self.loadFromStream(stream, os.path.basename(configFile))

        # User strings are currently parsed. This is mainly due to re-using
        # the loadUserMappings() function which
        # for mappingStr, extra in self.loadUserMappings().values():
        #     log.debug("User mapping: %r (extra: %r)", mappingStr, extra)
        #     # self.tryLoadMapping(mappingStr, "User", extra=extra)
        #     self.database

        self._loaded = True

    def tryLoadMapping(
        self, mappingString: str, source: str, extra: str = ""
    ) -> Optional[GameControllerMapping]:
        try:
            mapping = self.parseMapping(mappingString)
        except Exception:
            log.exception("Exception while parsing mapping")
        else:
            mapping.source = source
            mapping.extra = extra
            self.mappings[mapping.guid] = mapping
            log.info(
                "Loaded controller mapping for %r from %r with extra %r",
                mapping.guid,
                mapping.source,
                mapping.extra,
            )
            return mapping
        return None

    def loadFromStream(self, stream: IO[bytes], source: str) -> None:
        for lineBytes in stream.readlines():
            try:
                line = lineBytes.decode("UTF-8").strip()
            except Exception:
                log.exception("Exception while decoding mapping")
            else:
                if line and not line.startswith("#"):
                    # self.tryLoadMapping(line, source)
                    if len(line) > 32 and line[32] == ",":
                        guid = line[:32].lower()
                        if guid in self.database:
                            log.debug("%r: Skipping %r", source, guid)
                        else:
                            self.database[guid] = (line, source, "")

    def getMapping(self, deviceGuid: str) -> Optional[GameControllerMapping]:
        try:
            return self.mappings[deviceGuid]
        except KeyError:
            if deviceGuid in self.database:
                mappingString, source, extra = self.database[deviceGuid]
                mapping = self.tryLoadMapping(
                    mappingString, source=source, extra=extra
                )
                return mapping
            # FIXME: Or exception or None?
            # mapping = GameControllerMapping()
            # mapping.source = ""
            # return mapping

            # Add None to the loaded mappings cache so we don't try to parse
            # again and again in case of parsing error.
            self.mappings[deviceGuid] = None
            return None

    def parseMapping(self, mappingStr: str) -> GameControllerMapping:
        mapping = GameControllerMapping.fromString(mappingStr)
        return mapping

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
                        log.debug("Found extra for %r: %r", guid, extra)
                        mappings[guid] = (mappings[guid][0], extra)
                    else:
                        log.debug(
                            "Ignoring extra for %r: %r (guid was %r)",
                            lastGuid,
                            extra,
                            guid,
                        )
        
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
