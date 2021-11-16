import hashlib
import logging
import logging.config
import os
import shutil
import tarfile
import tempfile
from typing import List, Tuple

import requests
from typing_extensions import TypedDict

import fsboot
from fscore.system import System
from fscore.tasks import Task
from fsgamesys.product import Product
from system.utilities.updater.checkforupdatestask import Update

log = logging.getLogger(__name__)


class UpdateResult(TypedDict):
    restartRequired: bool


# @traced
class UpdateTask(Task[UpdateResult]):
    def __init__(self, updates: List[Update]) -> None:
        super().__init__()
        self.updates = updates

    def main(self) -> UpdateResult:
        self.setProgress("Starting update")
        restartRequired = False
        for update in sorted(self.updates, key=self.sortUpdatesBy):
            # if self.isCancelled():
            #     return
            self.maybeCancel()
            self.downloadAndExtractUpdate(update)
            # if self.isCancelled():
            #     return
            self.maybeCancel()
            if self.installUpdate(update["packageName"]):
                # FIXME: Update was installed
                pass
            else:
                # Update was not installed, restart required
                restartRequired = True
        return {"restartRequired": restartRequired}
        # self.setResult({"restartRequired": restartRequired})

    def sortUpdatesBy(self, update: Update) -> Tuple[bool, str]:
        """Sort updates so Launcher updates are done at the end. The Launcher
        update is slightly more complicated and requires a restart."""
        isLauncher = update["packageName"].endswith("-Launcher")
        return (isLauncher, update["packageName"])

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

    def downloadAndExtractUpdate(self, update: Update) -> None:
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
    ) -> None:
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

    def verifyArchive(self, path: str, sha256: str) -> bool:
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
    ) -> bool:
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

    def validateRelativeName(self, packageName: str, name: str) -> None:
        if name != packageName and not name.startswith(f"{packageName}/"):
            raise Exception(
                f"Archive member {name} does not start with {packageName}/"
            )
        if ".." in name:
            raise Exception(f"Archive member {name} includes '..'")

    def isLauncherUpdate(self, packageName: str) -> bool:
        return packageName == Product.getLauncherPluginName()

    def installUpdate(self, packageName: str) -> bool:
        """Installs package from `PackageName.next` to `PackageName`"""
        if self.isLauncherUpdate(packageName):
            if System.isWindows() or True:
                self.installUpdateWindows(packageName)
                return False

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
        return True

    def installUpdateWindows(self, packageName: str) -> None:
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

    def installUpdateWindows2(self, packageName: str) -> None:
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
                if os.path.exists(dstPath) or os.path.islink(dstPath):
                    self.removeOrRename(dstPath)
                print("Copy", srcPath, "->", dstPath)
                shutil.copy(srcPath, dstPath, follow_symlinks=False)
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

    def removeOrRename(self, path: str) -> None:
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

    def createFileList(self, dir: str) -> List[str]:
        # fileList = set()
        # We use a list here to keep the order. When we delete remaining
        # entries, we want to delete in reverse order so parent directories
        # are deleted at the end.
        fileList: List[str] = []
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
