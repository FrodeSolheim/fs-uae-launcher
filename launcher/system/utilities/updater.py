import hashlib
import logging
import logging.config
import os
import shutil
import sys
import tarfile
import tempfile
import time
from configparser import ConfigParser
from typing import Optional

import requests
from autologging import TRACE, traced

import fsui
from fscore.system import System
from fscore.version import Version
from fsgamesys.product import Product
from launcher.fswidgets2.button import Button
from launcher.fswidgets2.flexcontainer import (
    FlexContainer,
    VerticalFlexContainer,
)
from launcher.fswidgets2.imageview import ImageView
from launcher.fswidgets2.label import Label
from launcher.fswidgets2.spacer import Spacer
from launcher.fswidgets2.textarea import TextArea
from launcher.fswidgets2.window import Window
from launcher.i18n import gettext
from launcher.system.classes.windowcache import WindowCache
from launcher.system.prefs.update import Update
from launcher.system.special.login import WidgetSizeSpinner
from launcher.system.special.logout import AsyncTaskRunner, Task

log = logging.getLogger(__name__)

# logging.basicConfig(
#     level=TRACE,
#     stream=sys.stdout,
#     format="%(levelname)s:%(name)s:%(funcName)s:%(message)s",
# )

# 'logging.config.dictConfig(
#     {
#         "version": 1,
#         "formatters": {
#             "logformatter": {
#                 # "format": "%(asctime)s:%(levelname)s:%(name)s:%(funcName)s:%(message)s",
#                 # "format": "%(name)s:%(funcName)s:%(message)s",
#                 "format": "%(message)s",
#             },
#             "traceformatter": {
#                 # "format": "%(asctime)s:%(process)s:%(levelname)s:%(filename)s:"
#                 # "%(lineno)s:%(name)s:%(funcName)s:%(message)s",
#                 "format": "%(name)s:%(funcName)s:%(message)s",
#             },
#         },
#         "handlers": {
#             "loghandler": {
#                 "class": "logging.FileHandler",
#                 "level": logging.DEBUG,
#                 "formatter": "logformatter",
#                 "filename": "app.log",
#             },
#             "tracehandler": {
#                 "class": "logging.StreamHandler",
#                 "level": TRACE,
#                 "formatter": "traceformatter",
#                 "stream": sys.stdout,
#                 # "filename": "trace.log",
#             },
#         },
#         "loggers": {
#             "launcher.system": {
#                 "level": TRACE,
#                 "handlers": ["tracehandler", "loghandler"],
#             },
#         },
#     }
# )'


@traced
def wsopen(window=None, **kwargs):
    return Updater.open(window, **kwargs)


@traced
class Updater:
    @staticmethod
    def open(window: Window = None, **kwargs):
        updaterWindow = WindowCache.open(UpdaterWindow, centerOnWindow=window)
        if updaterWindow.checkForUpdatesButton.isEnabled():
            updaterWindow.checkForUpdates()

    @staticmethod
    def getSystemDirectory() -> str:
        return os.path.join(fsboot.base_dir(), "System")

    @staticmethod
    def getPluginVersionFromDirectory(pluginDir) -> str:
        configParser = ConfigParser()
        configParser.read(os.path.join(pluginDir, "Plugin.ini"))
        return configParser.get("plugin", "version")

    @staticmethod
    def getPluginDirectory(pluginName):
        systemDir = Updater.getSystemDirectory()
        return os.path.join(systemDir, pluginName)

    @staticmethod
    def getPluginVersion(pluginName) -> Optional[str]:
        configParser = ConfigParser()
        pluginDir = Updater.getPluginDirectory(pluginName)
        pluginIni = os.path.join(pluginDir, "Plugin.ini")
        if not os.path.exists(pluginIni):
            return None
        configParser.read(pluginIni)
        return configParser.get("plugin", "version")


@traced
class UpdaterWindow(Window):
    def __init__(self):
        super().__init__(
            title=gettext("Updater"),
            minimizable=False,
            maximizable=False,
            style={"backgroundColor": "#bbbbbb"},
        )

        self.updates = None

        with FlexContainer(
            parent=self,
            style={
                "gap": 20,
                "padding": 20,
                "paddingBottom": 10,
            },
        ):
            with VerticalFlexContainer(style={"flexGrow": 1, "gap": 5}):
                Label(
                    gettext("Software updater"),
                    style={"fontWeight": "bold"},
                )
                Label(gettext("Updates the Launcher and plugins for you"))
            ImageView(fsui.Image("workspace:/data/48/plugins.png"))
        self.textArea = TextArea(
            parent=self,
            readOnly=True,
            style={
                "margin": 20,
                "marginTop": 10,
                "marginBottom": 10,
                "width": 600,
                "height": 200,
            },
        )
        with FlexContainer(
            parent=self,
            style={
                "gap": 10,
                "padding": 20,
                "paddingTop": 10,
            },
        ):
            self.preferencesButton = Button(
                gettext("Preferences"), onClick=self.onPreferences
            )
            Spacer(style={"flexGrow": 1})
            # self.errorLabel = Label(style={"flexGrow": 1})
            # FIXME: Set visible via stylesheet instead?
            self.spinner = WidgetSizeSpinner(visible=False)
            self.checkForUpdatesButton = Button(
                gettext("Check for updates"), onClick=self.checkForUpdates
            )
            self.updateAllButton = Button(
                gettext("Update all"), onClick=self.updateAll
            )

        self.updateAllButton.disable()
        # self.textArea.appendText("Heisann")
        # self.textArea.appendText("Hopsann")

    def onPreferences(self):
        Update.open(openedFrom=self.getWindow())

    def appendLogLine(self, line):
        self.textArea.appendLine(line)

    # FIXME: Move to widget
    def addEventListener(self, eventName, listener):
        if eventName == "destroy":
            self.destroyed.connect(listener)

    # FIXME: Move to widget
    def addDestroyListener(self, listener):
        self.destroyed.connect(listener)

    # FIXME: Move to widget
    def onDestroy(self, listener):
        self.destroyed.connect(listener)

    def setRunning(self, running):
        if running:
            self.checkForUpdatesButton.disable()
            self.updateAllButton.disable()

    def checkForUpdates(self):
        self.setRunning(True)

        @traced
        def onResult(result):
            self.checkForUpdatesButton.enable()

            self.appendLogLine("Got result, doing calculations...")
            updates = findUpdates(result)
            for update in updates:
                systems = set()
                for archive in update["archives"]:
                    systems.update(archive["systems"])
                    # for osName in archive.get("operatingSystems", []):
                    #     for archName in archive.get("architectures", []):
                    #         systems.add(f"{osName}_{archName}")
                    # operatingSystems.update(
                    #     archive.get("operatingSystems", [])
                    # )
                    # operatingSystems.update(
                    #     archive.get("operatingSystems", [])
                    # )
                self.appendLogLine(
                    "{}: {} => {} ({})".format(
                        update["packageName"],
                        update["installedVersion"],
                        update["availableVersion"],
                        ", ".join(sorted(systems)),
                    )
                )
            if len(updates) > 0:
                self.appendLogLine("Updates are available!")
            else:
                self.appendLogLine("No updates!")
            self.updateAllButton.enable(len(updates) > 0)
            self.updates = updates

            # if self.updateAllButton.isEnabled():
            #     self.updateAll()

        @traced
        def onError(error):
            self.checkForUpdatesButton.enable()
            # self.setRunning(False)
            self.appendLogLine(f"Error: {str(error)}")
            # self.errorLabel.setText(f"Error: {str(error)}")

        @traced
        def onProgress(progress, *, task):
            # self.errorLabel.setText(progress)
            self.appendLogLine(progress)
            # task.cancel()

        self.addDestroyListener(
            AsyncTaskRunner(onResult, onError, onProgress)
            .run(CheckForUpdatesTask())
            .cancel,
        )

        # FIXME: Add support for (also) inheriting from AsyncTaskRunner?
        # self.runTask(LogoutTask(authToken), onResult, onError, onProgress)

    def updateAll(self):
        if self.updates is None:
            log.warning("updateAll: self.updates was None")
            return
        self.setRunning(True)

        @traced
        def onResult(result):
            self.checkForUpdatesButton.enable()
            if result["restartRequired"]:
                self.appendLogLine(
                    "Update complete, but a restart is required"
                )
            else:
                self.appendLogLine("Update complete")

        @traced
        def onError(error):
            self.checkForUpdatesButton.enable()
            # self.setRunning(False)
            self.appendLogLine(f"Error: {str(error)}")
            # self.errorLabel.setText(f"Error: {str(error)}")

        @traced
        def onProgress(progress, *, task):
            # self.errorLabel.setText(progress)
            self.appendLogLine(progress)
            # task.cancel()

        self.addDestroyListener(
            AsyncTaskRunner(onResult, onError, onProgress)
            .run(UpdateTask(self.updates))
            .cancel,
        )


@traced
def findUpdates(availableUpdates):
    log.debug("Checking packages updates")

    def checkRequirement(version, name, value):
        validValues = version.get(name, [])
        print("Check", value, "against", validValues)
        if len(validValues) > 0 and value not in validValues:
            return False
        return True

    def getCurrentArchitecture():
        return System.getCpuArchitecture()

    def getCurrentBranch():
        # FIXME
        return "Master"

    def getCurrentOperatingSystem():
        return System.getOperatingSystem()

    def getInstalledVersion(packageName) -> Optional[str]:
        if packageName == Product.getLauncherPluginName():
            if fsboot.development():
                # We don't want the fake version number to confuse the
                # updater in development mode.
                pass
            else:
                from launcher.version import VERSION

                return VERSION
        return Updater.getPluginVersion(packageName)

    def checkSystemRequirement(version, value):
        validValues = version.get("systems", [])
        print("Check", value, "against", validValues)
        if len(validValues) > 0 and value not in validValues:
            return False
        return True

    def findAvailableUpdate(packageUpdates):
        operatingSystem = System.getOperatingSystem()
        cpuArchitecture = System.getCpuArchitecture()
        currentSystem = f"{operatingSystem}_{cpuArchitecture}"
        for version in packageUpdates["versions"]:
            if not checkSystemRequirement(version, currentSystem):
                continue
            # if (
            #     not checkRequirement(
            #         version, "architectures", getCurrentArchitecture()
            #     )
            #     or not checkRequirement(
            #         version, "branches", getCurrentBranch()
            #     )
            #     or not checkRequirement(
            #         version, "operatingSystems", getCurrentOperatingSystem()
            #     )
            # ):
            #     continue
            return version

    updates = []

    for packageName in sorted(availableUpdates["packages"]):
        packageUpdates = availableUpdates["packages"][packageName]
        installedVersion = getInstalledVersion(packageName)
        if installedVersion is None:
            log.debug("Package %s is not installed, ignored", packageName)
            continue
        availableUpdate = findAvailableUpdate(packageUpdates)
        if availableUpdate is None:
            log.debug("No relevant update for package %s", packageName)
            continue
        availableVersion = availableUpdate["version"]
        print(repr(availableVersion))
        print(repr(installedVersion))
        includeUpdate = False
        if availableVersion == installedVersion:
            log.debug("No relevant update for package %s", packageName)
        # if Version(availableVersion) == Version(installedVersion):
        #     pass
        elif Version(availableVersion) > Version(installedVersion):
            log.info(
                "Package %s: Version %s => %s",
                packageName,
                installedVersion,
                availableVersion,
            )
            downgrade = False
            includeUpdate = True
        else:
            log.info(
                "Package %s: Version %s => %s DOWNGRADE",
                packageName,
                installedVersion,
                availableVersion,
            )
            downgrade = True
            includeUpdate = True

        # FIXME: If more than one os/arch was installed for a package,
        # Also calculate information about installing those as well?
        if includeUpdate:
            updates.append(
                {
                    "packageName": packageName,
                    "installedVersion": installedVersion,
                    "availableVersion": availableVersion,
                    "isDowngrade": False,
                    "archives": [availableUpdate],
                }
            )
    return updates


class CheckForUpdatesTask(Task):
    def main(self):
        self.setProgress("Getting list of updates...")
        if Product.is_fs_uae():
            r = requests.get("https://fs-uae.net/launcher/updates.json")
        else:
            r = requests.get("https://openretro.org/launcher/updates.json")
        return r.json()
        return {
            "packages": {
                "FS-UAE-Launcher": {
                    "versions": [
                        {
                            "branches": ["Master", "Stable", "Dev"],
                            "systems": ["Linux_x86-64"],
                            "version": "4.0.53-dev",
                            "url": "https://github.com/FrodeSolheim/fs-uae-launcher/releases/download/v4.0.53-dev/FS-UAE-Launcher_4.0.53-dev_Linux_x86-64.tar.xz",
                            "checksums": {
                                "sha256": "0d88d9d622370c1dbf86aa0886d71df9c1a92b5ee9990dfe3ec0fd338c652890"
                            },
                        },
                        {
                            "branches": ["Master", "Stable", "Dev"],
                            "systems": ["macOS_x86-64"],
                            "version": "4.0.53-dev",
                            "url": "https://github.com/FrodeSolheim/fs-uae-launcher/releases/download/v4.0.53-dev/FS-UAE-Launcher_4.0.53-dev_Linux_x86-64.tar.xz",
                            "checksums": {
                                "sha256": "b636b370f2964028534a376c06b6c765cc8bb55a3607495c9a6adcb6276a4cd0"
                            },
                        },
                        {
                            "branches": ["Master", "Stable", "Dev"],
                            "systems": ["Windows_x86-64"],
                            "version": "4.0.53-dev",
                            "url": "https://github.com/FrodeSolheim/fs-uae-launcher/releases/download/v4.0.53-dev/FS-UAE-Launcher_4.0.53-dev_macOS_x86-64.tar.xz",
                            "checksums": {
                                "sha256": "9c792fdae2169fd7176d940e866bf19f64e96467934b47c9c04187614548512d"
                            },
                        },
                    ]
                },
                "Mednafen": {
                    "versions": [
                        {
                            "branches": ["Master", "Stable", "Dev"],
                            "systems": ["Linux_x86-64"],
                            "version": "1.26.1.16-fs",
                            "url": "https://github.com/FrodeSolheim/mednafen/releases/download/v1.26.1.16-fs/Mednafen_1.26.1.16-fs_Linux_x86-64.tar.xz",
                            "checksums": {
                                "sha256": "9fb9758b7a37c6c90bc5752e4ca5c19fb367c3a495b70170cb703870d9b340ba"
                            },
                        },
                        {
                            "branches": ["Master", "Stable", "Dev"],
                            "systems": ["macOS_x86-64"],
                            "version": "1.26.1.16-fs",
                            "url": "https://github.com/FrodeSolheim/mednafen/releases/download/v1.26.1.16-fs/Mednafen_1.26.1.16-fs_macOS_x86-64.tar.xz",
                            "checksums": {
                                "sha256": "c92fb5c9d21904e77759b84629c9d11b50231f396c4da233d76e54bf41b764a3"
                            },
                        },
                        {
                            "branches": ["Master", "Stable", "Dev"],
                            "systems": ["Windows_x86-64"],
                            "version": "1.26.1.16-fs",
                            "url": "https://github.com/FrodeSolheim/mednafen/releases/download/v1.26.1.16-fs/Mednafen_1.26.1.16-fs_Windows_x86-64.tar.xz",
                            "checksums": {
                                "sha256": "f4acf255f3c2a4a6085f5143f6b578ed8395090a3af695bc5ef4ef71e14402ab"
                            },
                        },
                    ]
                },
            }
        }


import fsboot


@traced
class UpdateTask(Task):
    def __init__(self, updates):
        super().__init__()
        self.updates = updates

    def sortUpdatesBy(self, update):
        """Sort updates so Launcher updates are done at the end. The Launcher
        update is slightly more complicated and requires a restart."""
        isLauncher = update["packageName"].endswith("-Launcher")
        return (isLauncher, update["packageName"])

    def main(self):
        self.setProgress("Starting update")
        restartRequired = False
        for update in sorted(self.updates, key=self.sortUpdatesBy):
            if self.isCancelled():
                return
            self.downloadAndExtractUpdate(update)
            if self.isCancelled():
                return
            if self.installUpdate(update["packageName"]):
                # FIXME: Update was installed
                pass
            else:
                # Update was not installed, restart required
                restartRequired = True
        return {"restartRequired": restartRequired}

    def getInstallDirectory(self, packageName: str) -> str:
        # FIXME: This should be centralized somewhere
        systemDirectory = os.path.join(fsboot.getBaseDirectory(), "System")
        return systemDirectory

    def getPackageDirectory(self, packageName: str) -> str:
        return os.path.join(self.getInstallDirectory(packageName), packageName)

    def getPackageNextDirectory(self, packageName: str) -> str:
        return os.path.join(
            self.getInstallDirectory(packageName), f"{packageName}.next"
        )

    def getPackagePartialDirectory(self, packageName: str) -> str:
        return os.path.join(
            self.getInstallDirectory(packageName), f"{packageName}.partial"
        )

    def downloadAndExtractUpdate(self, update):
        """Downloads and extracts package into `PackageName.next` directory"""
        packageName = update["packageName"]
        nextDir = self.getPackageNextDirectory(packageName)
        if os.path.exists(nextDir):
            assert nextDir.endswith(".next")
            shutil.rmtree(nextDir)
        partialDir = self.getPackagePartialDirectory(packageName)
        if os.path.exists(partialDir):
            assert partialDir.endswith(".partial")
            shutil.rmtree(partialDir)
        os.makedirs(partialDir)
        try:
            for archive in update["archives"]:
                if self.isCancelled():
                    return
                self.downloadAndExtractArchive(
                    partialDir,
                    packageName,
                    archive["url"],
                    archive["checksums"]["sha256"],
                )
            os.rename(f"{partialDir}/{packageName}", nextDir)
        finally:
            log.info(f"Cleaning up {partialDir}")
            shutil.rmtree(partialDir)

    def downloadAndExtractArchive(
        self, installDir: str, packageName: str, url: str, sha256: str
    ):
        fileName = url.rsplit("/", 1)[-1].split("?", 1)[0]
        self.setProgress(f"Downloading {fileName}...")
        tempFile = tempfile.NamedTemporaryFile(suffix=fileName, delete=False)
        try:
            with tempFile:
                with requests.get(url, stream=True) as r:
                    shutil.copyfileobj(r.raw, tempFile)
            size = os.path.getsize(tempFile.name)
            self.setProgress(f"Downloaded {size} bytes, verying checksum...")
            if not self.verifyArchive(tempFile.name, sha256):
                # self.setProgress(f"Checksum verification FAILED")
                raise Exception("Checksum verification failed")
            self.setProgress(f"Checksum OK")
            self.extractArchive(
                installDir, packageName, fileName, tempFile.name
            )
        finally:
            os.remove(tempFile.name)

    def verifyArchive(self, path, sha256):
        hashObject = hashlib.sha256()
        with open(path, "rb") as f:
            while True:
                data = f.read(1024 * 1024)
                if not data:
                    break
                hashObject.update(data)
        return hashObject.hexdigest() == sha256

    def extractArchive(
        self,
        installDir: str,
        packageName: str,
        archiveName: str,
        archivePath: str,
    ):
        if self.isCancelled():
            return False
        log.info(f"Extracting {archivePath} to {installDir}")
        self.setProgress(f"Extracting {archiveName}...")
        with tarfile.open(name=archivePath) as tarFile:
            for tarInfo in tarFile.getmembers():
                if self.isCancelled():
                    return False
                self.validateRelativeName(packageName, tarInfo.name)
                log.info(f"Extracting {tarInfo.name}")
                tarFile.extract(tarInfo, installDir)
        return True

    def validateRelativeName(self, packageName, name):
        if name != packageName and not name.startswith(f"{packageName}/"):
            raise Exception(
                f"Archive member {name} does not start with {packageName}/"
            )
        if ".." in name:
            raise Exception(f"Archive member {name} includes '..'")

    def isLauncherUpdate(self, packageName):
        return packageName == Product.getLauncherPluginName()

    def installUpdate(self, packageName):
        """Installs package from `PackageName.next` to `PackageName`"""
        if self.isLauncherUpdate(packageName):
            if System.isWindows() or True:
                return self.installUpdateWindows(packageName)

        # if self.isLauncherUpdate(packageName):
        #     log.info("Launcher update is not installed now (restart)")
        #     self.setProgress("Launcher update is postponed for restart")
        #     return False
        self.setProgress(f"Installing update for {packageName}")
        packageDir = self.getPackageDirectory(packageName)
        nextDir = self.getPackageNextDirectory(packageName)
        if os.path.exists(packageDir):
            oldDir = f"{packageDir}.old"
            if not os.path.exists(oldDir):
                os.makedirs(oldDir)
            # Find an available name inside `package.old` directory which we can do
            # an atomic rename to, and even in some cases rename also when e.g.
            # Windows have mapped the files to memory.
            k = 0
            while True:
                oldPackageDir = os.path.join(oldDir, str(k))
                if not os.path.exists(oldPackageDir):
                    break
                # log.info("Removing directory {oldDir}")
                # shutil.rmtree(oldDir)
            log.info(f"Renaming directory {packageDir} -> {oldPackageDir}")
            # FIXME: Try catch on this, if failing, tell user to restart the
            # Launcher instead?
            try:
                os.rename(packageDir, oldPackageDir)
            except Exception:
                log.exception("Could not move away old package")
                # FIXME: Register that a restart is needed
                self.setProgress(
                    f"A restart is needed for the upgrade of {packageName}"
                )
                return False
            # Try to delete old dir, but do not fail if not successful
            try:
                shutil.rmtree(oldDir)
            except Exception:
                log.exception(f"Failed to completely clean up {oldDir}")
        log.info(f"Renaming directory {nextDir} -> {packageDir}")
        os.rename(nextDir, packageDir)
        return False

    def installUpdateWindows(self, packageName):
        self.setProgress(f"Installing update for {packageName}....")
        try:
            self.installUpdateWindows2(packageName)
        except Exception as e:
            self.setProgress(
                f"WARNING: A failure occurred during installation of "
                f"{packageName} and it may now be in an inconsistent state."
            )
            self.setProgress(
                f"You should download and re-install {packageName} manually!"
            )
            self.setProgress(
                "FIXME: Write about .next directory and manually moving it "
                "into place. Also suggest to open Explorer for the user?"
            )
            raise e

    def installUpdateWindows2(self, packageName):
        srcDir = self.getPackageNextDirectory(packageName)
        dstDir = self.getPackageDirectory(packageName)
        dstFileList = self.createFileList(dstDir)

        for dirPath, dirNames, fileNames in os.walk(srcDir):
            relativeDirPath = dirPath[len(srcDir) + 1 :]
            # print("relative", relativeDirPath)
            for dirName in dirNames:
                dstPath = os.path.join(dstDir, relativeDirPath, dirName)
                print(f"Ensuring directory {dstPath}")
                if not os.path.exists(dstPath):
                    os.makedirs(dstPath)
                try:
                    dstFileList.remove(os.path.normcase(dstPath))
                except ValueError:
                    pass
            for fileName in fileNames:
                srcPath = os.path.join(srcDir, relativeDirPath, fileName)
                dstPath = os.path.join(dstDir, relativeDirPath, fileName)
                # path = os.path.normpath(os.path.join(dirPath, fileName))
                # fileList.add(f"path/")
                # fileList.append(path)
                if os.path.exists(dstPath):
                    self.removeOrRename(dstPath)
                print(f"Copying -> {dstPath}")
                shutil.copy(srcPath, dstPath)
                try:
                    dstFileList.remove(os.path.normcase(dstPath))
                except ValueError:
                    pass

        print("Remaining entries", dstFileList)
        for path in reversed(dstFileList):
            print(f"File/dir is remaining: {path}")
            if os.path.isfile(path):
                try:
                    self.removeOrRename(path)
                except IOError:
                    print(f"Failed to delete remaining file {path}")
                    # FIXME: Register for future deletion?
            if os.path.isdir(path):
                try:
                    print(f"Removing directory {path}")
                    os.rmdir(path)
                except IOError:
                    print(f"Failed to delete remaining directory {path}")
                    # FIXME: Register for future deletion?

        # Finally, if successful, rename source directory
        self.setProgress(f"Cleaning up...")
        print(f"Deleting directory {srcDir} recursively...")
        shutil.rmtree(srcDir)

    def removeOrRename(self, path):
        try:
            print(f"Trying to remove file {path}")
            os.remove(path)
        except IOError:
            print(f"Could not remove file {path}")
            # If this does not work, an exception will be thrown
            print(f"Trying to rename file {path}")
            newPath = f"{path}.__del__"
            k = 1
            while os.path.exists(newPath):
                k += 1
                newPath = f"{path}.{k}.__del__"
            os.rename(path, newPath)

    def createFileList(self, dir):
        # fileList = set()
        # We use a list here to keep the order. When we delete remaining
        # entries, we want to delete in reverse order so parent directories
        # are deleted at the end.
        fileList = []
        for dirPath, dirNames, fileNames in os.walk(dir):
            for dirName in dirNames:
                path = os.path.normcase(
                    os.path.normpath(os.path.join(dirPath, dirName))
                )
                # fileList.add(path)
                fileList.append(path)
            for fileName in fileNames:
                path = os.path.normcase(
                    os.path.normpath(os.path.join(dirPath, fileName))
                )
                # fileList.add(path)
                fileList.append(path)
        return fileList
