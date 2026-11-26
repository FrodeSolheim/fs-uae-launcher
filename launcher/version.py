"""The version of FS-UAE Launcher, and where this build comes from.

The builds (python -m build, and make dist for the source tarball) write
launcher/build_info.py with the version and the identity of the build (see
build/version.py), which is not in the repository. Without it, the launcher
runs from a git checkout (or a copy of the source): the version is made from
VERSION.FS and git the same way, and the build is unofficial.

build_header() is logged at the top of the log file (fsbc/init.py).
"""

import importlib.util
import os
import platform
import sys
from pathlib import Path
from typing import List

# The version the build was made for, such as 3.2.36 for a release, or
# 3.2.36-dev.20261126T1656+gb96cb28950 for a development build.
VERSION = "0.0.0"
# The whole hash of the commit the build was made from.
COMMIT = "unknown"
# Who made the build, such as "Official build (FrodeSolheim/fs-uae-launcher,
# GitHub Actions run 1234567890)". It is self-declared.
ORIGIN = "Unofficial build"
BUILD_DATE = "unknown"
BUILD_ENVIRONMENT = "unknown"


def _source_dir() -> str:
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _version_from_source() -> None:
    """Sets VERSION and COMMIT from VERSION.FS and git, with
    build/version.py, which is in the checkout but not in the builds."""
    global VERSION, COMMIT
    source_dir = _source_dir()
    try:
        with open(os.path.join(source_dir, "VERSION.FS")) as f:
            VERSION = f.read().strip()
    except OSError:
        return
    script = os.path.join(source_dir, "build", "version.py")
    if not os.path.exists(os.path.join(source_dir, ".git")):
        return
    if not os.path.exists(script):
        return
    try:
        spec = importlib.util.spec_from_file_location(
            "_fs_uae_launcher_build_version", script
        )
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        VERSION = module.dist_version(Path(source_dir))
        COMMIT = module.commit(Path(source_dir))
    except Exception as e:
        print(
            f"WARNING: Could not make the version from git: {e}",
            file=sys.stderr,
        )


try:
    from launcher import build_info  # type: ignore
except ImportError:
    _version_from_source()
else:
    VERSION = build_info.VERSION
    COMMIT = build_info.COMMIT
    ORIGIN = build_info.ORIGIN
    BUILD_DATE = build_info.BUILD_DATE
    BUILD_ENVIRONMENT = build_info.BUILD_ENVIRONMENT


def is_development_version(version: str = "") -> bool:
    """Whether the version (by default VERSION) is a development version,
    <major>.<minor>.<revision>-dev.<date>T<time>+g<hash>."""
    return "-dev." in (version or VERSION)


def base_version(version: str = "") -> str:
    """The version (by default VERSION) without the pre-release part and the
    build metadata: 3.2.36 for 3.2.36-dev.20261126T1656+gb96cb28950."""
    return (version or VERSION).split("+", 1)[0].split("-", 1)[0]


def _running_with() -> str:
    parts = [f"Python {platform.python_version()}"]
    try:
        from PyQt6.QtCore import PYQT_VERSION_STR, qVersion

        parts.append(f"Qt {qVersion()} (PyQt6 {PYQT_VERSION_STR})")
    except Exception:
        pass
    frozen = " (frozen)" if getattr(sys, "frozen", False) else ""
    return f"{', '.join(parts)}{frozen}, on {platform.platform()}"


def build_header() -> List[str]:
    """The lines of the build header, which says what the build is and
    where it comes from; logged at the top of the log file."""
    return [
        f"FS-UAE Launcher version {VERSION}",
        f"  Origin: {ORIGIN}",
        f"  Commit: {COMMIT}",
        f"  Build date: {BUILD_DATE}",
        f"  Build environment: {BUILD_ENVIRONMENT}",
        f"  Running with: {_running_with()}",
    ]
