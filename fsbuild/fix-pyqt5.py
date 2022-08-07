#!/usr/bin/env python3
import os
import shutil
import sys

from PyQt5.QtCore import QLibraryInfo


def main() -> None:
    # This is mainly to avoid bundling libraries that can cause issues,
    # such as GTK (and dependencies) being included if GTK platform
    # integration is included.
    print("Fixing PyQt5 installation before running pyinstaller")
    print("(Removing unnecessary stuff")

    # libraries_path = QLibraryInfo.location(QLibraryInfo.LibrariesPath)
    # print(libraries_path)

    def remove_path(path: str) -> None:
        print(path)
        if os.path.exists(path):
            print("Removing", path)
            shutil.rmtree(path)

    qml_path = QLibraryInfo.location(QLibraryInfo.Qml2ImportsPath)
    remove_path(qml_path)

    translations_path = QLibraryInfo.location(QLibraryInfo.TranslationsPath)
    remove_path(translations_path)

    plugins_path = QLibraryInfo.location(QLibraryInfo.PluginsPath)
    print(plugins_path)

    def remove_plugins(type: str) -> None:
        plugin_type_path = os.path.join(plugins_path, type)
        print(plugin_type_path)
        if os.path.exists(plugin_type_path):
            print("Removing", plugin_type_path)
            shutil.rmtree(plugin_type_path)

    if sys.platform == "linux":
        remove_plugins("platformthemes")


if __name__ == "__main__":
    main()
