# Builds, versions and releases

Every build of FS-UAE Launcher knows its version, who made it and from which
commit, and logs this in the build header at the top of its log file.

## Reading a version

`VERSION.FS` holds the version being worked towards: the next release, not
the last one. Every other version is made from it (`build/version.py`):

| Version | What it is |
| --- | --- |
| `3.2.36` | A release: the commit tagged `v3.2.36`. |
| `3.2.36-dev.20261126T1656+gb96cb28950` | A development build on the way to 3.2.36, made from the commit alone: its committer date and time in UTC (to the minute), and its hash. Every build of a commit that is not a release gets it, whoever makes it and wherever, also from a shallow clone. |

The versions follow [Semantic Versioning](https://semver.org/):
`3.2.35` < `3.2.36-dev.20261126T1656` < `3.2.36-dev.20261127T0905` <
`3.2.36`, and everything after `+` is ignored when comparing. Debian and RPM
packages made from the source tarball use `~` for `-`.

`python3 build/version.py` prints the version of the checkout (`--commit`
the commit, `--base` the `VERSION.FS` version).

## Kinds of builds

| Build | Version | File name | Origin | Where to get it |
| --- | --- | --- | --- | --- |
| Releases | `3.2.36` | `FS-UAE-Launcher_3.2.36_<os>_<arch>.<ext>` | `Official build (FrodeSolheim/fs-uae-launcher, GitHub Actions run <run ID>)` | GitHub Releases, with `SHA256SUMS` |
| The `dev` pre-release (the latest push to `main`) | `3.2.36-dev.<date>T<time>+g<hash>` | `FS-UAE-Launcher_dev_<os>_<arch>.<ext>`; the version is in the title, the notes and the first line of `SHA256SUMS` | as above | [The `dev` pre-release](https://github.com/FrodeSolheim/fs-uae-launcher/releases/tag/dev) |
| Workflow artifacts (pushes, tags, manual runs) | the development version, or the release version for a tag | `FS-UAE-Launcher_<version>_<os>_<arch>.<ext>` | as above | The run's page under Actions |
| Workflow artifacts of pull requests | the development version of the pull request's commit | as above | `Unofficial build (FrodeSolheim/fs-uae-launcher, GitHub Actions run <run ID>, pull request <n>)` | The pull request's checks |
| Workflow artifacts in forks | as above | as above | `Unofficial build (<owner>/<repository>, GitHub Actions run <run ID>)` | The fork's runs |
| Local builds (`python -m build all`) | as above | as above | `Unofficial build`, unless `FSUAE_LAUNCHER_BUILD_ORIGIN` is set | Made by whoever runs them |
| Running from a git checkout (`./fs-uae-launcher`) | the development version, made from git at startup | - | `Unofficial build` | - |
| The source tarball (`make dist-xz`) and what is built from it | the version when the tarball was made | `fs-uae-launcher-<version>.tar.xz` | `Unofficial build` (packagers may change `launcher/build_info.py`) | Releases have one |

`<os>_<arch>` is `Linux_x86-64`, `Linux_ARM64`, `Windows_x86-64`,
`macOS_x86-64` or `macOS_ARM64`; the extension is `.tar.xz` for Linux, `.zip`
for Windows and `.dmg` for macOS.

## The build header

The launcher logs the build header first, so that it is at the top of the
log file (`fs-uae-launcher.log.txt` in `Cache/Logs` in the FS-UAE base
directory) and of stdout:

```text
FS-UAE Launcher version 3.2.36-dev.20261126T1656+gb96cb28950
  Origin: Official build (FrodeSolheim/fs-uae-launcher, GitHub Actions run 1234567890)
  Commit: b96cb28950cdba8504238a36a19d6a53af824f18
  Build date: 2026-11-26 17:10:07 UTC
  Build environment: Ubuntu 22.04.5 LTS; GitHub Actions runner image ubuntu22 20261109.1.0
  Running with: Python 3.12.15, Qt 6.9.0 (PyQt6 6.9.0) (frozen), on Linux-6.8.0-1017-azure-x86_64-with-glibc2.35
```

The build writes the version and identity to `launcher/build_info.py` (not
in the repository) just before PyInstaller bundles the app, and removes it
afterwards, so that a checkout that runs from source makes its version from
git. The identity comes from the environment variables
`FSUAE_LAUNCHER_BUILD_ORIGIN` (default `Unofficial build`),
`FSUAE_LAUNCHER_BUILD_ENVIRONMENT` (default: the operating system and the
GitHub runner image) and `SOURCE_DATE_EPOCH` (the build date; default now).

The origin is self-declared: anyone can make a build that says "Official
build". What proves where a download comes from is the macOS signature
(Developer ID, notarized) and the `SHA256SUMS` on the release page.

## The dist workflow

`.github/workflows/dist.yml` builds every platform and the source tarball for
pushes, pull requests, tags and manual runs.

- **macOS signing** (`FSUAE_MACOS_SIGNING`, see `macos_signing()` in
  `build/__main__.py`): `required` for `v*` tags, and for pushes to `main`
  and manual runs on `main` of `FrodeSolheim/fs-uae-launcher` (these fail
  without the signing secrets); `auto` for `main` in forks (signed when the
  secrets are there, otherwise unsigned with a warning); `off` for pull
  requests and other branches (signed ad hoc). The signing works as for
  FS-UAE's macOS dists, with the same secrets and environment variables:
  `MACOS_CERTIFICATE_P12` (the Developer ID Application certificate with its
  key, a `.p12` file in base64) and `MACOS_CERTIFICATE_PASSWORD`, which
  `build/macos-signing-keychain` puts in a temporary keychain
  (`FSUAE_MACOS_KEYCHAIN`), and `NOTARYTOOL_APPLE_ID`,
  `NOTARYTOOL_PASSWORD` and `NOTARYTOOL_TEAM_ID` for notarization. The
  identity is `Developer ID Application: Frode Solheim (<team ID>)`. On a
  Mac with the certificate in the login keychain, `python -m build all`
  signs when the `NOTARYTOOL_*` variables are set.
- **The `dev` pre-release**: for every push to `main` of
  `FrodeSolheim/fs-uae-launcher`, when every build has passed, the
  `dev-release` job replaces the files of the `dev` pre-release
  (`build/release_files.py --dev`, `build/dev_release.py`) and moves the
  `dev` tag to the commit. It is never marked as the latest release. A run
  whose builds fail leaves the previous build there, and a build of an
  earlier push that finishes later does not replace a newer one. Since the
  tag moves, `git fetch --tags` in a clone with an older `dev` tag needs
  `--force`.

## Making a release

1. Check that `VERSION.FS` has the version to release, that the
   `Version <version>:` section of `ChangeLog` is complete, and that the dist
   workflow passed for the commit.
2. Tag the commit and push the tag:

   ```sh
   git tag -a v3.2.36 -m "FS-UAE Launcher 3.2.36"
   git push origin v3.2.36
   ```

3. The dist workflow builds the tag. A tag that is not `v<version>` for
   `VERSION.FS` fails the builds. When every build and the source tarball
   are done, the `release` job makes a **draft** GitHub Release of the tag
   with the archives, the source tarball and `SHA256SUMS`
   (`build/release_files.py`, `build/draft-release`). Nothing is published
   automatically; running the workflow again for the tag replaces the
   draft's files.
4. Check the draft: download the files, run `sha256sum -c SHA256SUMS`, start
   them and check the build header (`FS-UAE Launcher version 3.2.36`,
   `Origin: Official build ...`).
5. Edit the title and notes, and publish the release.
6. Bump the version for the next cycle, in one commit: `VERSION.FS` to the
   next version, a new `Version <next>:` section at the top of `ChangeLog`,
   and the version in `pyproject.toml`, `uv.lock` (the
   `fs-uae-launcher-3` package), the first line of `debian/changelog` and
   `fsbuild_version` in `fs-uae-launcher.spec`. (`setup.py` reads
   `VERSION.FS`, and `make dist` sets the Debian and RPM versions of the
   source tarball itself.)

To fix a failed tag build before the release is published, delete the draft
(if any) and the tag, fix the problem on `main`, and tag again. After the
release is published, its tag is never moved.
