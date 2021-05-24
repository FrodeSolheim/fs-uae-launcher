#!/usr/bin/env python3

import logging
import os
import shutil
import socket
import subprocess
import sys
import traceback
from configparser import ConfigParser
from typing import List, Optional

import fsboot
import fsgamesys
import launcher.version
from fsbc.init import initialize_application
from fscore.settings import Settings
from fscore.system import System
from fscore.version import Version
from fsgamesys.product import Product
from launcher.apps.launcher2 import wsopen_main
from launcher.option import Option
from launcher.version import VERSION
from system.utilities.updater.updateutil import UpdateUtil

log = logging.getLogger(__name__)


outputDebugString = None


def debug(message: str) -> None:
    global outputDebugString
    if sys.platform == "win32":
        if outputDebugString is None:
            import ctypes

            outputDebugString = ctypes.windll.kernel32.OutputDebugStringW
        outputDebugString(message)
    print(message)


def check_python_version() -> None:
    if sys.version_info[0] < 3 or sys.version_info[1] < 6:
        debug("You need at least Python 3.6 to run FS-UAE Launcher")
        sys.exit(1)


def setup_fsgs_pythonpath() -> None:
    fsgs_pythonpath = os.environ.get("FSGS_PYTHONPATH")
    if fsgs_pythonpath:
        sys.path.insert(0, fsgs_pythonpath)


def fix_mingw_path() -> None:
    if os.getcwd().startswith("C:\\msys64\\home\\"):
        os.environ["PATH"] = "C:\\msys64\\mingw64\\bin;" + os.environ["PATH"]


def setup_frozen_qpa_platform_plugin_path() -> None:
    if not fsboot.is_frozen():
        return
    # os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = os.path.join(
    #     fsboot.executable_dir(), "platforms"
    # )


def setup_frozen_requests_ca_cert() -> None:
    if not fsboot.is_frozen():
        return
    data_dirs = [fsboot.executable_dir()]
    data_dir = os.path.abspath(
        os.path.join(fsboot.executable_dir(), "..", "..", "Data")
    )
    debug(data_dir)
    debug(str(os.path.exists(data_dir)))
    if os.path.exists(data_dir):
        data_dirs.append(data_dir)
    else:
        data_dir = os.path.abspath(
            os.path.join(
                fsboot.executable_dir(), "..", "..", "..", "..", "..", "Data"
            )
        )
        debug(data_dir)
        debug(str(os.path.exists(data_dir)))
        if os.path.exists(data_dir):
            data_dirs.append(data_dir)
    for data_dir in data_dirs:
        path = os.path.join(data_dir, "cacert.pem")
        if os.path.exists(path):
            debug("[HTTP] Using {}".format(path))
            os.environ["REQUESTS_CA_BUNDLE"] = path
            break


# FIXME: Move to update module?
def getLauncherPluginName() -> str:
    """Returns name like FS-UAE-Launcher or OpenRetro-Launcher"""
    return Product.getLauncherPluginName()


def getLauncherPluginDirectory() -> str:
    return UpdateUtil.getPluginDirectory(getLauncherPluginName())


# FIXME: Move to update module
def getPluginOldDirectory(pluginDir: str) -> str:
    return f"{pluginDir}.old"


# FIXME: Move to update module
def cleanPluginOldDirectory(pluginDir: str) -> bool:
    pluginOldDir = getPluginOldDirectory(pluginDir)
    if not os.path.exists(pluginOldDir):
        return True
    # Try to delete old dir, but do not fail if not successful
    debug(f"Delete {pluginOldDir}")
    try:
        shutil.rmtree(pluginOldDir)
        return True
    except Exception:
        debug(f"Failed to completely clean up {pluginOldDir}")
        log.exception("Failed to completely clean up {pluginOldDir}")
        return False


def cleanLauncherOldDirectory() -> bool:
    return cleanPluginOldDirectory(getLauncherPluginDirectory())


# FIXME: Move to update module
def moveOldPluginDirectory(pluginDir: str) -> bool:
    debug(f"Move away old plugin directory {pluginDir}")
    pluginOldDir = getPluginOldDirectory(pluginDir)
    if not os.path.exists(pluginOldDir):
        os.makedirs(pluginOldDir)
    # Find an available name inside `Plugin.old` directory which we can do an
    # atomic rename to, and even in some cases rename also when e.g. Windows
    # have mapped the files to memory.
    k = 0
    while True:
        pluginOldNumberedDir = os.path.join(pluginOldDir, str(k))
        if not os.path.exists(pluginOldNumberedDir):
            break
        # log.info("Removing directory {oldDir}")
        # shutil.rmtree(oldDir)
    debug(f"Renaming directory {pluginDir} -> {pluginOldNumberedDir}")
    # FIXME: Try catch on this, if failing, tell user to restart the
    # Launcher instead?
    try:
        os.rename(pluginDir, pluginOldNumberedDir)
    except Exception:
        debug("Could not move away old package")
        log.exception("Could not move away old package")
        # FIXME: Register that a restart is needed
        # self.setProgress(
        #     f"A restart is needed for the upgrade of {packageName}"
        # )
        return False
    # Try to delete old dir, but do not fail if not successful
    cleanPluginOldDirectory(pluginDir)
    return True


def findLauncherExecutable(pluginDir: str):
    binDir = os.path.join(
        pluginDir, System.getOperatingSystem(), System.getCpuArchitecture()
    )
    pluginName = getLauncherPluginName()
    exeName = pluginName.lower()
    if System.windows:
        executable = os.path.join(binDir, f"{exeName}.exe")
    elif System.macos:
        executable = os.path.join(
            binDir, f"{pluginName}.app", "Contents", "MacOS", exeName
        )
    else:
        executable = os.path.join(binDir, exeName)
    if os.path.exists(executable):
        debug(f"Plugin launcher executable {executable} exists")
        return executable
    else:
        debug(f"Plugin launcher executable {executable} does not exist")
        return None


class Options:
    redirect: Optional[bool] = None


def maybeRunNewerVersionFromPlugin():
    launcherDir = getLauncherPluginDirectory()

    # launcherNextDir = f"{launcherDir}.next"
    # if os.path.exists(launcherNextDir):
    #     debug(f"{launcherNextDir} exists")
    #     if os.path.exists(launcherDir):
    #         debug(f"{launcherDir} exists, move away")
    #         if not moveOldPluginDirectory(launcherDir):
    #             debug(f"WARNING: Could not move {launcherDir}")

    #     if os.path.exists(launcherDir):
    #         # Was not moved away
    #         debug(f"Cannot install update for {pluginName}")
    #         # FIXME: GUI warning?
    #         log.warning(f"Cannot install update for {pluginName}")
    #     else:
    #         debug(f"Renaming directory {launcherNextDir} -> {launcherDir}")
    #         os.rename(launcherNextDir, launcherDir)

    if os.path.exists(launcherDir):
        if Options.redirect is False:
            debug("Will continue using current executable")
            return False
        # FIXME: Move to fscore.version?
        from fscore.version import Version
        from launcher.version import VERSION

        try:
            pluginVersion = UpdateUtil.getPluginVersionFromDirectory(
                launcherDir
            )
            if Version(pluginVersion) > Version(VERSION):
                debug(
                    f"Plugin version ({pluginVersion}) "
                    f"> running version ({VERSION})"
                )
            else:
                debug(
                    f"Plugin version ({pluginVersion}) "
                    f"<= running version ({VERSION})"
                )
                if Options.redirect is True:
                    debug("Older version, but redirect == 1")
                else:
                    return False
        except Exception:
            traceback.print_exc()
            debug("Problem comparing Launcher version")
            if Options.redirect is True:
                debug("Cannot redirect, but redirect == 1")
                sys.exit(1)
            else:
                return False

        if fsboot.development():
            print(Options.redirect)
            if Options.redirect is True:
                debug("Development mode, but redirect == 1")
            else:
                debug("Development mode, will not run plugin executable")
                return False

        launcherExecutable = findLauncherExecutable(launcherDir)
        if launcherExecutable is None:
            return False

        # Make sure pending output is flushed before we effectively put things
        # on pause
        sys.stdout.flush()
        sys.stderr.flush()

        args = sys.argv.copy()
        args[0] = launcherExecutable
        # FIXME: Could make sure we send full path here, but the option value
        # isn't really that important.
        # FIXME: fsboot.executable?
        args.append("--redirected-from=" + sys.executable)
        # Make sure the new process does not try to redirect
        args.append("--no-redirect")
        debug(f"Running new process with args {repr(args)}")
        completedProcess = subprocess.run(args)
        returnCode = completedProcess.returncode
        debug(f"Child process (redirected) return value: {returnCode}")
        sys.exit(returnCode)


def configureLauncherApp(
    base_name: str,
    databases: List[str],
    default_platform_id: str,
    default_titlebar_color: Optional[str],
):
    print(
        "configureLauncherApp",
        base_name,
        databases,
        default_platform_id,
        default_titlebar_color,
    )
    Product.base_name = base_name
    for option_name in fsgamesys.OPENRETRO_DEFAULT_DATABASES:
        Option.get(option_name)["default"] = "0"
        Settings.set_default(option_name, "0")
    for option_name in [
        Option.AMIGA_DATABASE,
        Option.CD32_DATABASE,
        Option.CDTV_DATABASE,
    ]:
        Option.get(option_name)["default"] = "0"
        Settings.set_default(option_name, "0")
    for option_name in databases:
        Option.get(option_name)["default"] = "1"
        Settings.set_default(option_name, "1")

    from fsgamesys.config.config import Config

    Config.set_default("platform", default_platform_id)
    Product.default_platform_id = default_platform_id

    if default_titlebar_color is not None:
        Settings.set_default(
            "launcher_titlebar_bgcolor", default_titlebar_color
        )
    # Settings.set_default("launcher_titlebar_fgcolor", "#cccccc")
    import fsboot

    fsboot.set("base_dir_name", base_name)
    # return "SYS:Launcher"


def handleArgument(key: str, value: str):
    global _redirect
    if key == "fake-version":
        # This will raise an exception (on purpose) if the version number
        # cannot be parsed.
        Version(value)
        launcher.version.VERSION = value
    elif key == "redirect":
        if value == "1":
            Options.redirect = True
        elif value == "0":
            Options.redirect = False
        elif value == "":
            Options.redirect = None
        else:
            raise Exception("Unknown value for redirect")


def handleArguments() -> None:
    # for i, arg in enumerate(sys.argv[1:]):
    for arg in sys.argv[1:]:
        print("ARG", arg)
        if arg.startswith("--"):
            arg = arg[2:]
            if arg.startswith("-no-"):
                arg = arg[4:]
                assert not "=" in arg
                value = "0"
            try:
                key, value = arg.split("=", 1)
            except ValueError:
                key = arg
                value = "1"
            print(key, value)
            handleArgument(key, value)


def printOption(option: str, description: str = ""):
    print(" ", option, end="")
    padding = 40 - 2 - len(option) - 1
    if padding > 0:
        print(" " * padding, end="")
    print(description)


def printHelp() -> None:
    print("FIXME Launcher vFIXME")
    print("")

    print("Command arguments:")
    printOption("--help")
    printOption("--version")
    print("")

    print("Maybe implement (FIXME):")
    printOption("--disable-updates", "Or --no-updates?")
    print("")

    print("For debugging/testing (not guaranteed to be stable):")
    printOption(
        "--fake-version[=<version>]", "Useful for testing update system"
    )
    printOption("--redirect")
    print("")

    print("FIXME: ADD MORE INFO HERE")


def print_version() -> None:
    print(launcher.version.VERSION)


def main(*, app: str, brand: str):
    try:
        handleArguments()
    except Exception as e:
        # FIXME: Use pyqt or tkinter to show GUI error message?
        # from tkinter import messagebox
        # messagebox.showerror("Title", "Message")
        # FIXME: fscore.fatal module?
        raise e

    if "--version" in sys.argv:
        print_version()
        sys.exit(0)

    if "--help" in sys.argv:
        printHelp()
        sys.exit(0)

    # If successful, this call (using execv) will not return
    # FIXME: Problem using exec with PyQT on macOS (dual loaded QT libraries)
    # FIXME: Exec does not work smoothly on Windows (new process does not
    # replace current one, so synchronously waiting on the original does
    # not work when it is replaced.
    if maybeRunNewerVersionFromPlugin():
        # Should not reach this point...
        sys.exit(1)
    else:
        debug("Will continue using current executable")

    # sys.exit()
    check_python_version()
    setup_fsgs_pythonpath()
    fix_mingw_path()
    setup_frozen_qpa_platform_plugin_path()
    setup_frozen_requests_ca_cert()

    if app == "Launcher":
        Product.base_name = brand
        if brand == "OpenRetro":
            configureLauncherApp(
                "OpenRetro",
                fsgamesys.OPENRETRO_DEFAULT_DATABASES,
                "amiga",
                # "#945ebe",
                # "#444444",
                None,
            )
            appName = "openretro-launcher"
        else:
            appName = "fs-uae-launcher"
        cleanLauncherOldDirectory()
        initialize_application(appName, version=VERSION)
        # app_main = partial(wsopen_main, app)
        if len(sys.argv) > 1 and ":" in sys.argv[1]:
            return wsopen_main(sys.argv[1])
        return wsopen_main("SYS:Launcher")

    # if app == "openretro-launcher":
    #     pass

    if app == "fs-uae-arcade":
        pass
    elif app == "fs-uae-launcher":
        import launcher.apps

        launcher.apps.main()
    elif app == "fs-fuse-launcher":
        import launcher.apps

        launcher.apps.main("fs-fuse-launcher")
    elif app == "fs-mame-launcher":
        import launcher.apps

        launcher.apps.main("fs-mame-launcher")
    elif app == "openretro-launcher":
        import launcher.apps

        launcher.apps.main("openretro-launcher")
    else:
        raise Exception(f"Unknown app {app}")


if __name__ == "__main__":
    main(app="Launcher", brand="FS-UAE")
