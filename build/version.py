#!/usr/bin/env python3
"""Prints the version of a build of FS-UAE Launcher, from VERSION.FS and git.

Usage: version.py [--commit | --base] [<project directory>]
       version.py --write-build-info <path> [--version <version>] [--source]
                  [<project directory>]

VERSION.FS holds the version being worked towards (the next release; it is
bumped right after a release). The version of a build is made from it and
the commit:

- Tag build: the commit has the tag v<version>, and the version is
  <version>. A commit with another v* tag (and none for the version) fails,
  so that a release cannot be made with the wrong version.
- Other builds: <version>-dev.<YYYYMMDD>T<HHMM>+g<hash>, for example
  3.2.36-dev.20261126T1656+gb96cb28950, where the date and time (to the
  minute) are the commit's committer date in UTC, and the hash is the
  commit's abbreviated hash (10 or more digits). It is made from the commit
  alone, so the same commit gets the same version wherever and by whoever it
  is built, also from a shallow clone. Who made a build is its origin
  (below), not its version.

The versions follow Semantic Versioning: 3.2.35 < 3.2.36-dev.20261126T1656
< 3.2.36, and the build metadata (+g<hash>) does not count when comparing.
The date and time are one identifier, with a "T" between them as in ISO
8601, so that the time keeps its leading zero and the identifier sorts as
text in date order.

With --commit, it prints the whole hash of the checked-out commit instead,
and with --base the VERSION.FS version. With --write-build-info, it writes
the version and the identity of the build to a Python file, as
launcher/build_info.py has them, and prints the version (--source for a
source tarball, see build_info()).

The build script (python -m build, build/__main__.py) and make dist
(Makefile) write launcher/build_info.py with it, which the launcher reads at
run time (launcher/version.py) and logs in the build header at the top of
its log file. The identity of a build comes from these environment
variables, all optional:

- FSUAE_LAUNCHER_BUILD_ORIGIN: who made the build (default "Unofficial
  build"). The dist workflow sets it to "Official build
  (FrodeSolheim/fs-uae-launcher, GitHub Actions run <run ID>)" for the
  repository's own runs.
- FSUAE_LAUNCHER_BUILD_ENVIRONMENT: what the build was made in (default: the
  operating system, and the GitHub Actions runner image when there is one).
- SOURCE_DATE_EPOCH: the build date (default: now).

Uses Python 3.9 and the standard library alone, since launcher/version.py
also runs it when the launcher runs from a git checkout.
"""

from __future__ import annotations

import argparse
import os
import platform
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

# The tags of releases, the ones that make a build a tag build.
TAG_PATTERN = "v*"
DEFAULT_ORIGIN = "Unofficial build"
# What an origin or a build environment may have in it.
IDENTITY_CHARS = r"A-Za-z0-9 .,:;()/+_#@=~-"
IDENTITY_PATTERN = re.compile(rf"^[{IDENTITY_CHARS}]{{1,200}}$")


class VersionError(Exception):
    pass


def default_project_dir() -> Path:
    return Path(__file__).resolve().parents[1]


def git(project_dir: Path, *args: str) -> str:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=project_dir,
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError as e:
        raise VersionError(f"cannot run git: {e}") from e
    if result.returncode != 0:
        raise VersionError(
            f"git {' '.join(args)} failed in {project_dir} (the version is "
            "made with git, so the build must be made from a git "
            f"checkout): {result.stderr.strip()}"
        )
    return result.stdout.strip()


def base_version(project_dir: Path) -> str:
    """The version in VERSION.FS, <major>.<minor>.<revision>."""
    path = project_dir / "VERSION.FS"
    try:
        text = path.read_text().strip()
    except OSError as e:
        raise VersionError(f"cannot read {path}: {e}") from e
    if re.fullmatch(r"\d+\.\d+\.\d+", text) is None:
        raise VersionError(
            f"{path} must have a version <major>.<minor>.<revision>, "
            f"not {text!r}"
        )
    return text


def dist_version(project_dir: Path) -> str:
    version = base_version(project_dir)
    tags = git(
        project_dir, "tag", "--points-at", "HEAD", "--list", TAG_PATTERN
    ).split()
    tagged = f"v{version}" in tags
    if tags and not tagged:
        raise VersionError(
            f"the commit is tagged {', '.join(tags)}, but the version in "
            f"VERSION.FS is {version}: a tag build needs the tag v{version}"
        )
    if tagged:
        return version
    # The committer date (not the author date: a rebased or cherry-picked
    # commit is a new commit), and the hash with 10 digits or more, so that
    # a fresh clone, where git may pick another default length, names the
    # same commit the same way.
    timestamp, commit_hash = git(
        project_dir, "log", "-1", "--abbrev=10", "--format=%ct %h"
    ).split()
    date = datetime.fromtimestamp(int(timestamp), timezone.utc)
    return f"{version}-dev.{date:%Y%m%dT%H%M}+g{commit_hash}"


def commit(project_dir: Path) -> str:
    """The whole hash of the checked-out commit."""
    return git(project_dir, "rev-parse", "--verify", "HEAD")


def _checked_identity(name: str, value: str) -> str:
    if IDENTITY_PATTERN.match(value) is None:
        raise VersionError(
            f"{name} may only have letters, digits and ' .,:;()/+_#@=~-', "
            f"at most 200 characters: {value!r}"
        )
    return value


def build_origin() -> str:
    value = os.environ.get("FSUAE_LAUNCHER_BUILD_ORIGIN", "")
    return _checked_identity(
        "FSUAE_LAUNCHER_BUILD_ORIGIN", value or DEFAULT_ORIGIN
    )


def _operating_system() -> str:
    if sys.platform == "linux":
        try:
            with open("/etc/os-release", encoding="UTF-8") as f:
                for line in f:
                    if line.startswith("PRETTY_NAME="):
                        return line.split("=", 1)[1].strip().strip('"')
        except OSError:
            pass
        return "Linux"
    if sys.platform == "darwin":
        return f"macOS {platform.mac_ver()[0]}".strip()
    if sys.platform == "win32":
        return f"Windows {platform.version()}".strip()
    return platform.system() or "unknown"


def build_environment() -> str:
    """What the build is made in: the operating system, and the GitHub
    Actions runner image when the build runs there (GitHub's runners set
    ImageOS and ImageVersion)."""
    value = os.environ.get("FSUAE_LAUNCHER_BUILD_ENVIRONMENT", "")
    if not value:
        parts = [_operating_system()]
        image_os = os.environ.get("ImageOS", "")
        image_version = os.environ.get("ImageVersion", "")
        if image_os:
            parts.append(
                f"GitHub Actions runner image {image_os} {image_version}"
            )
        # Leaves out anything unexpected rather than fail on it.
        value = re.sub(rf"[^{IDENTITY_CHARS}]", "", "; ".join(parts))
        value = value.strip()[:200] or "unknown"
    return _checked_identity("FSUAE_LAUNCHER_BUILD_ENVIRONMENT", value)


def build_date() -> str:
    epoch = os.environ.get("SOURCE_DATE_EPOCH", "")
    if epoch:
        date = datetime.fromtimestamp(int(epoch), timezone.utc)
    else:
        date = datetime.now(timezone.utc)
    return f"{date:%Y-%m-%d %H:%M:%S} UTC"


def build_info(
    project_dir: Path, version: str = "", source: bool = False
) -> dict[str, str]:
    """The version and identity of a build of the checkout, as
    launcher/build_info.py has them. The version is the dist version unless
    given. For a source tarball (source), the origin is "Unofficial build"
    and the build date and environment unknown, since whoever builds or
    installs from it makes the build (and may change the file)."""
    return {
        "VERSION": version or dist_version(project_dir),
        "COMMIT": commit(project_dir),
        "ORIGIN": DEFAULT_ORIGIN if source else build_origin(),
        "BUILD_DATE": "unknown" if source else build_date(),
        "BUILD_ENVIRONMENT": "unknown" if source else build_environment(),
    }


def write_build_info(path: Path, info: dict[str, str]) -> None:
    lines = [
        "# The version of this build of FS-UAE Launcher, and where it comes",
        "# from. Written by the build (build/version.py); not in the",
        "# repository (see launcher/version.py).",
    ]
    lines.extend(f"{key} = {value!r}" for key, value in info.items())
    path.write_text("\n".join(lines) + "\n", encoding="UTF-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--commit",
        action="store_true",
        help="print the checked-out commit's whole hash instead",
    )
    group.add_argument(
        "--base",
        action="store_true",
        help="print the VERSION.FS version instead",
    )
    group.add_argument(
        "--write-build-info",
        metavar="PATH",
        type=Path,
        help="write the build info to PATH, and print the version",
    )
    parser.add_argument(
        "--version",
        default="",
        help="with --write-build-info: the version (default: the dist "
        "version)",
    )
    parser.add_argument(
        "--source",
        action="store_true",
        help="with --write-build-info: for a source tarball",
    )
    parser.add_argument(
        "project_dir",
        nargs="?",
        type=Path,
        default=default_project_dir(),
        help="the project directory (default: the one this script is in)",
    )
    args = parser.parse_args()
    try:
        if args.commit:
            print(commit(args.project_dir))
        elif args.base:
            print(base_version(args.project_dir))
        elif args.write_build_info:
            info = build_info(args.project_dir, args.version, args.source)
            write_build_info(args.write_build_info, info)
            print(info["VERSION"])
        else:
            print(dist_version(args.project_dir))
    except VersionError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
