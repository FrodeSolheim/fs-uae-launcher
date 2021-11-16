import logging
import logging.config
from typing import Dict, List, Optional, cast

import requests
from typing_extensions import TypedDict

from fscore.system import System
from fscore.tasks import Task
from fscore.version import Version
from fsgamesys.product import Product
from system.utilities.updater.updateutil import UpdateUtil

log = logging.getLogger(__name__)


class Checksums(TypedDict):
    sha256: str


class PackageVersion(TypedDict):
    branches: List[str]
    checksums: Checksums
    systems: List[str]
    version: str
    url: str


# class AvailableUpdate(TypedDict):
#     checksums: Checksums
#     systems: List[str]
#     url: str


AvailableUpdate = PackageVersion


class Update(TypedDict):
    packageName: str
    installedVersion: str
    availableVersion: str
    isDowngrade: bool
    archives: List[AvailableUpdate]


class Package(TypedDict):
    versions: List[PackageVersion]


class CheckForUpdatesResult(TypedDict):
    packages: Dict[str, Package]


class CheckForUpdatesTask(Task[CheckForUpdatesResult]):
    def main(self) -> CheckForUpdatesResult:
        self.setProgress("Getting list of updates...")
        if Product.is_fs_uae():
            r = requests.get("https://fs-uae.net/launcher/updates.json")
        else:
            r = requests.get("https://openretro.org/launcher/updates.json")
        # FIXME: Implement real parsing/validation
        return cast(CheckForUpdatesResult, r.json())

    @staticmethod
    def findUpdates(availableUpdates: CheckForUpdatesResult) -> List[Update]:
        log.debug("Checking packages updates")

        # FIXME: Not currently used
        # def checkRequirement(
        #     version: PackageVersion, name: str, value: str
        # ) -> bool:
        #     validValues = version.get(name, [])
        #     print("Check", value, "against", validValues)
        #     if len(validValues) > 0 and value not in validValues:
        #         return False
        #     return True

        def getCurrentArchitecture() -> str:
            return System.getCpuArchitecture()

        # FIXME: Not currently used - check branch!
        # def getCurrentBranch() -> str:
        #     # FIXME
        #     return "Master"

        def getCurrentOperatingSystem() -> str:
            return System.getOperatingSystem()

        def getInstalledVersion(packageName: str) -> Optional[str]:
            if packageName == Product.getLauncherPluginName():
                # if fsboot.development():
                #     # We don't want the fake version number to confuse the
                #     # updater in development mode.
                #     pass
                # else:
                #     from launcher.version import VERSION

                #     return VERSION
                from launcher.version import VERSION

                return VERSION
            return UpdateUtil.getPluginVersion(packageName)

        def checkSystemRequirement(
            version: PackageVersion, value: str
        ) -> bool:
            validValues = version.get("systems", [])
            print("Check", value, "against", validValues)
            if len(validValues) > 0 and value not in validValues:
                return False
            return True

        def findAvailableUpdate(
            packageUpdates: Package,
        ) -> Optional[PackageVersion]:
            operatingSystem = getCurrentOperatingSystem()
            cpuArchitecture = getCurrentArchitecture()
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
            return None

        updates: List[Update] = []

        for packageName in sorted(availableUpdates["packages"]):
            packageUpdates = availableUpdates["packages"][packageName]
            installedVersion = getInstalledVersion(packageName)
            if installedVersion is None:
                wantPackages = ["FS-UAE", "CAPSImg"]
                if Product.is_fs_uae():
                    wantPackages.extend(["QEMU-UAE"])
                wantPackage = packageName in wantPackages
                if wantPackage:
                    log.debug(
                        "Package %s is not installed, but want it", packageName
                    )
                    installedVersion = "0"
                else:
                    log.debug(
                        "Package %s is not installed, ignored", packageName
                    )
                    continue
            availableUpdate = findAvailableUpdate(packageUpdates)
            if availableUpdate is None:
                log.debug("No relevant update for package %s", packageName)
                continue
            availableVersion = availableUpdate["version"]
            print(repr(availableVersion))
            print(repr(installedVersion))
            includeUpdate = False
            downgrade: bool
            if availableVersion == installedVersion:
                log.debug("No relevant update for package %s", packageName)
                # if Version(availableVersion) == Version(installedVersion):
                #     pass
                continue
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
                # includeUpdate = True
                # No downgrades for now...
                includeUpdate = False

            # FIXME: If more than one os/arch was installed for a package,
            # Also calculate information about installing those as well?
            if includeUpdate:
                updates.append(
                    {
                        "packageName": packageName,
                        "installedVersion": installedVersion,
                        "availableVersion": availableVersion,
                        "isDowngrade": downgrade,
                        "archives": [availableUpdate],
                    }
                )
        return updates
