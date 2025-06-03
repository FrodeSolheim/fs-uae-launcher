#!/usr/bin/env python3
import os
import shutil
import sys

from PyQt6.QtCore import QLibraryInfo


def main():
    # This is mainly to avoid bundling libraries that can cause issues,
    # such as GTK (and dependencies) being included if GTK platform
    # integration is included.
    print("Fixing PyQt6 installation before running pyinstaller")
    print("(Removing unnecessary stuff")

    # librariesPath = QLibraryInfo.location(QLibraryInfo.LibrariesPath)
    # print(librariesPath)

    def removePath(path):
        print(path)
        if os.path.exists(path):
            print("Removing", path)
            shutil.rmtree(path)

    qmlPath = QLibraryInfo.path(QLibraryInfo.LibraryPath.Qml2ImportsPath)
    removePath(qmlPath)

    translationsPath = QLibraryInfo.path(
        QLibraryInfo.LibraryPath.TranslationsPath
    )
    removePath(translationsPath)

    pluginsPath = QLibraryInfo.path(QLibraryInfo.LibraryPath.PluginsPath)
    print(pluginsPath)

    def removePlugins(type):
        pluginTypePath = os.path.join(pluginsPath, type)
        print(pluginTypePath)
        if os.path.exists(pluginTypePath):
            print("Removing", pluginTypePath)
            shutil.rmtree(pluginTypePath)

    if sys.platform == "linux":
        removePlugins("platformthemes")


if __name__ == "__main__":
    main()
