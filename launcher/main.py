#!/usr/bin/env python3
import os
import sys
import traceback

import launcher.version
from fsboot import executable_dir, is_frozen


def check_python_version():
    if sys.version_info[0] < 3 or sys.version_info[1] < 6:
        print("You need at least Python 3.6 to run FS-UAE Launcher")
        sys.exit(1)


def setup_fsgs_pythonpath():
    if os.environ.get("FSGS_PYTHONPATH", ""):
        sys.path.insert(0, os.environ.get("FSGS_PYTHONPATH"))


def fix_mingw_path():
    if os.getcwd().startswith("C:\\msys64\\home\\"):
        os.environ["PATH"] = "C:\\msys64\\mingw64\\bin;" + os.environ["PATH"]


def print_version():
    print(launcher.version.VERSION)


def setup_frozen_qpa_platform_plugin_path():
    if not is_frozen():
        return
    os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = os.path.join(
        fsboot.executable_dir(), "platforms"
    )


def setup_frozen_requests_ca_cert():
    if not is_frozen():
        return
    data_dirs = [fsboot.executable_dir()]
    data_dir = os.path.abspath(
        os.path.join(fsboot.executable_dir(), "..", "..", "Data")
    )
    print(data_dir, os.path.exists(data_dir))
    if os.path.exists(data_dir):
        data_dirs.append(data_dir)
    else:
        data_dir = os.path.abspath(
            os.path.join(
                fsboot.executable_dir(), "..", "..", "..", "..", "..", "Data"
            )
        )
        print(data_dir, os.path.exists(data_dir))
        if os.path.exists(data_dir):
            data_dirs.append(data_dir)
    for data_dir in data_dirs:
        path = os.path.join(data_dir, "cacert.pem")
        if os.path.exists(path):
            print("[HTTP] Using {}".format(path))
            os.environ["REQUESTS_CA_BUNDLE"] = path
            break


def main(*, app):
    if "--version" in sys.argv:
        print_version()
        sys.exit(0)
    check_python_version()
    setup_fsgs_pythonpath()
    fix_mingw_path()
    setup_frozen_qpa_platform_plugin_path()
    setup_frozen_requests_ca_cert()

    if app == "fs-uae-arcade":
        pass
    elif app == "fs-uae-launcher":
        import launcher.apps

        launcher.apps.main()
    else:
        raise Exception(f"Unknown app {app}")
