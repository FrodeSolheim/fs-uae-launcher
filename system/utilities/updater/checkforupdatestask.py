import logging
import logging.config
from typing import Optional

import requests

from fscore.system import System
from fscore.version import Version
from fsgamesys.product import Product
from system.special.logout import Task
from system.utilities.updater.updateutil import UpdateUtil

log = logging.getLogger(__name__)

import fsboot


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

    @staticmethod
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
            return UpdateUtil.getPluginVersion(packageName)

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
