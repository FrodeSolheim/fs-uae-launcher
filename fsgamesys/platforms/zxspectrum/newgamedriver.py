import subprocess
from typing import Dict, List, Optional


class Emulator:
    def __init__(self, executablePath):
        self.executablePath = executablePath


class Process(subprocess.Popen):
    pass


class IFileService:
    pass


class ISaveService:
    pass


class Config:

    def __init__(self):
        self.config = {}  # type: Dict[str, str]

    @property
    def zxSpectrumModel(self) -> str:
        return self.config.get("zxspectrum_model", "")
    
    @zxSpectrumModel.setter
    def zxSpectrumModel(self, value):
        self.config["zxspectrum_model"] = value


class GameDriver2:
    gameDriverVersion = 2
    emulatorName = "unknown"

    def __init__(self, config, emulator, fileService, saveService):
        self.config = config
        self.emulator = emulator
        self.fileService = fileService
        # self.gsContext = gsContext
        self.saveService = saveService
        self.runService = None

        self.process = None  # type: Optional[Process]

        self.args = []  # type: List[str]
        self.env = {}  # type: Dict[str, str]
        
        self._modelName = ""

    def logHeading(self, heading):
        print(heading)
        print("-" * 80)

    def setModelName(self, modelName: str):
        self._modelName = modelName

    def setEmulator(self, emulator: Emulator):
        self.emulator = emulator

    def setFileService(self, fileService: IFileService):
        self.fileService = fileService

    def setSaveService(self, saveService, ISaveService):
        self.saveService = saveService

    # def findEmulator(self, name: str) -> Emulator:
    #     pass

    def prepare(self):
        pass

    def run(self):
        self.runEmulator(
            emulator=self.findEmulator(self.emulatorName),
            args=self.args,
            env=self.setupEnvironment(self.env),
        )

    def setupEnvironment(self, env: Dict[str, str]) -> Dict[str, str]:
        pass

    def runEmulator(
        self, emulator: Emulator, args: List[str], env: Dict[str, str]
    ):
        self.process = None

    def cleanup(self):
        pass
