import os
import shutil
import subprocess
import sys
from pathlib import Path

from build import version as build_version
from build.lib import (
    arch_name,
    macos,
    os_name,
    run,
    windows,
    # rmtree_if_exists,
    getPackageInformation,
    getAppleCodesignIdentity,
    getAppleId,
    getApplePassword,
    getAppleTeamId,
    getBundlePath,
    getCodesignKeychainArgs,
    buildDmg,
    signDmg,
    notarizeApp,
    notarizeDmg,
    shell,
)

# Written for the build (build/version.py) and removed after it, so that a
# checkout that runs the launcher from source makes its version from git.
BUILD_INFO_PATH = "launcher/build_info.py"


def version():
    """Prints the version and the identity of a build of the checkout."""
    try:
        info = build_version.build_info(Path("."))
    except build_version.VersionError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    for key, value in info.items():
        print(f"{key}={value}")


def write_build_info():
    try:
        info = build_version.build_info(Path("."))
    except build_version.VersionError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    build_version.write_build_info(Path(BUILD_INFO_PATH), info)
    print(f"Wrote {BUILD_INFO_PATH}:")
    for key, value in info.items():
        print(f"  {key}={value}")


def bootstrap():
    run(["python", "./bootstrap"])


def configure():
    pass


def _remove_unwanted_pyqt_files(dir):
    for name in [
        # Linux
        "libgcc_s.so.1",
        # "libQt6Pdf.so.6",
        # "libQt6Svg.so.6",
        "libstdc++.so.6",
        # "PyQt6/Qt6/lib/libQt6Pdf.so.6",
        # "PyQt6/Qt6/lib/libQt6Svg.so.6",
        # Windows
        # "d3dcompiler_47.dll",
        # "libcrypto-1_1-x64.dll",
        # "libEGL.dll",
        # "libgcc_s_seh-1.dll",
        # "libGLESv2.dll",
        # "libssl-1_1-x64.dll",
        # "libstdc++-6.dll",
        # "libwinpthread-1.dll",
        # "opengl32sw.dll",
        # "PyQt6/Qt/plugins/bearer/qgenericbearer.dll",
        # "PyQt6/Qt/plugins/imageformats/qicns.dll",
        # "PyQt6/Qt/plugins/imageformats/qico.dll",
        # "PyQt6/Qt/plugins/imageformats/qtga.dll",
        # "PyQt6/Qt/plugins/imageformats/qtiff.dll",
        # "PyQt6/Qt/plugins/imageformats/qwbmp.dll",
        # "PyQt6/Qt/plugins/platforms/qminimal.dll",
        # "PyQt6/Qt/plugins/platforms/qoffscreen.dll",
        # "PyQt6/Qt/plugins/platforms/qwebgl.dll",
        # "PyQt6/QtNetwork.pyd",
        # "PyQt6/QtQml.pyd",
        # "PyQt6/QtQuick.pyd",
        # "Qt63DAnimation.dll",
        # "Qt63DCore.dll",
        # "Qt63DInput.dll",
        # "Qt63DLogic.dll",
        # "Qt63DQuickScene2D.dll",
        # "Qt63DRender.dll",
        # "Qt6Bluetooth.dll",
        # "Qt6Concurrent.dll",
        # "Qt6DBus.dll",
        # "Qt6Gamepad.dll",
        # "Qt6Location.dll",
        # "Qt6Multimedia.dll",
        # "Qt6MultimediaQuick.dll",
        # "Qt6Network.dll",
        # "Qt6Nfc.dll",
        # "Qt6Positioning.dll",
        # "Qt6PositioningQuick.dll",
        # "Qt6Qml.dll",
        # "Qt6QmlModels.dll",
        # "Qt6QmlWorkerScript.dll",
        # "Qt6Quick.dll",
        # "Qt6Quick3D.dll",
        # "Qt6Quick3DAssetImport.dll",
        # "Qt6Quick3DRender.dll",
        # "Qt6Quick3DRuntimeRender.dll",
        # "Qt6Quick3DUtils.dll",
        # "Qt6QuickControls2.dll",
        # "Qt6QuickParticles.dll",
        # "Qt6QuickShapes.dll",
        # "Qt6QuickTemplates2.dll",
        # "Qt6QuickTest.dll",
        # "Qt6RemoteObjects.dll",
        # "Qt6Sensors.dll",
        # "Qt6Sql.dll",
        # "Qt6Test.dll",
        # "Qt6WebChannel.dll",
        # "Qt6WebSockets.dll",
        # "Qt6WebView.dll",
        # "Qt6XmlPatterns.dll",
        # macOS
    ]:
        path = os.path.join(dir, name)
        if os.path.exists(path):
            os.remove(path)


def build():
    # Running make to create locales (among other things)
    run(["make"])

    build_dir = "build/_build"
    script_name = "fs-uae-launcher"

    dist_dir = f"{build_dir}/pyinstaller"
    if os.path.exists(dist_dir):
        shutil.rmtree(dist_dir)
    args = [
        "pyinstaller",
        "--specpath",
        "build/_build/spec",
        "--distpath",
        f"{dist_dir}",
        "--log-level",
        "DEBUG",
        "--collect-submodules",
        "OpenGL",
    ]
    if windows or macos:
        args.append("--windowed")
    if windows:
        args.extend(["--icon", "../../../icon/fs-uae-launcher.ico"])
    if macos:
        args.extend(
            ["--osx-bundle-identifier", "no.fengestad.fs-uae-launcher"]
        )
    args.extend(["--hidden-import", "launcher.build_info"])
    args.append(script_name)
    write_build_info()
    try:
        run(args)
    finally:
        os.remove(BUILD_INFO_PATH)
    internal_dir = os.path.join(dist_dir, "fs-uae-launcher", "_internal")

    _remove_unwanted_pyqt_files(os.path.join(internal_dir))


def bundle():
    # package_name = "fs-uae-launcher"
    # package_name_pretty = "FS-UAE-Launcher"
    # package_display_name = "FS-UAE Launcher"
    # macos_bundle_id = "no.fengestad.fs-uae-launcher"
    package = getPackageInformation()

    if macos:
        src_dir = f"build/_build/pyinstaller/{package.name}.app"
        app_dir = f"build/_build/{package.display_name}.app"
        if os.path.exists(app_dir):
            shutil.rmtree(app_dir)

        shutil.move(src_dir, app_dir)

        # os.makedirs(bin_bin)
        contents_dir = os.path.join(app_dir, "Contents")
        # os.makedirs(contents_dir)
        info_plist_file = os.path.join(contents_dir, "Info.plist")
        with open(info_plist_file, "w") as f:
            f.write(f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
  <dict>
    <key>CFBundleDisplayName</key>
    <string>{package.display_name}</string>
    <key>CFBundleExecutable</key>
    <string>{package.name}</string>
    <key>CFBundleIconFile</key>
    <string>{package.name}.icns</string>
    <key>CFBundleIdentifier</key>
    <string>{package.macos_bundle_id}</string>
    <key>CFBundleInfoDictionaryVersion</key>
    <string>6.0</string>
    <key>CFBundleName</key>
    <string>{package.display_name}</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>{package.simple_version}</string>
    <key>NSRequiresAquaSystemAppearance</key>
    <false/>
    <key>NSHighResolutionCapable</key>
    <true/>
  </dict>
</plist>
""")
        resources_dir = os.path.join(contents_dir, "Resources")
        shutil.copy(
            "icon/fs-uae-launcher.icns",
            os.path.join(resources_dir, "fs-uae-launcher.icns"),
        )

        locale_dir = os.path.join(resources_dir, "Locale")
    else:
        bundle_dir = f"build/_build/{package.pretty_name}"
        if os.path.exists(bundle_dir):
            shutil.rmtree(bundle_dir)
        bin_dir = os.path.join(bundle_dir, os_name, arch_name)

        src = f"build/_build/pyinstaller/{package.name}"
        # shutil.copytree(src, bin_dir, symlinks=True)
        shutil.move(src, bin_dir)

        resources_dir = os.path.join(bundle_dir, "Resources")
        os.makedirs(resources_dir)

        # Or put locale_dir in Resources?
        locale_dir = os.path.join(bundle_dir, "Locale")

    shutil.copytree("share/locale", locale_dir)

    for item in ["arcade", "fsgs", "launcher", "workspace"]:
        archive = shutil.make_archive(
            os.path.join(resources_dir, item),
            "zip",
            os.path.join("share", "fs-uae-launcher", "resources", item),
        )
        print(archive)


def macos_signing() -> bool:
    """Whether to sign the macOS app and .dmg with the Developer ID
    certificate and notarize them. As for FS-UAE's macOS dists: when the
    notarytool credentials (NOTARYTOOL_APPLE_ID, NOTARYTOOL_PASSWORD,
    NOTARYTOOL_TEAM_ID) are set and the keychain has the signing identity
    (getAppleCodesignIdentity), looked for in FSUAE_MACOS_KEYCHAIN when it
    is set (build/macos-signing-keychain sets it in CI), otherwise in the
    keychain search list. FSUAE_MACOS_SIGNING changes this: auto (the
    default) as above, required fails instead of making an unsigned build
    (for release builds), off never signs."""
    mode = os.environ.get("FSUAE_MACOS_SIGNING", "") or "auto"
    if mode not in ("required", "auto", "off"):
        print(
            "Error: FSUAE_MACOS_SIGNING must be auto, required or off, "
            f"not {mode}",
            file=sys.stderr,
        )
        sys.exit(1)
    if mode == "off":
        print(
            "WARNING: the macOS app and .dmg are not signed or notarized "
            "(FSUAE_MACOS_SIGNING=off)"
        )
        return False
    missing = [
        name
        for name, value in [
            ("NOTARYTOOL_APPLE_ID", getAppleId()),
            ("NOTARYTOOL_PASSWORD", getApplePassword()),
            ("NOTARYTOOL_TEAM_ID", getAppleTeamId()),
        ]
        if not value
    ]
    if not missing:
        identity = getAppleCodesignIdentity()
        keychain = os.environ.get("FSUAE_MACOS_KEYCHAIN", "")
        identities = subprocess.run(
            [
                "security",
                "find-identity",
                "-v",
                "-p",
                "codesigning",
                *([keychain] if keychain else []),
            ],
            capture_output=True,
            text=True,
            check=False,
        ).stdout
        if f'"{identity}"' not in identities:
            where = f" {keychain}" if keychain else ""
            missing.append(
                f'the signing identity "{identity}" in the keychain{where}'
            )
    if not missing:
        return True
    if mode == "required":
        print(
            "Error: cannot sign the macOS app (FSUAE_MACOS_SIGNING=required); "
            f"missing: {', '.join(missing)}",
            file=sys.stderr,
        )
        sys.exit(1)
    message = (
        "The macOS app and .dmg are not signed or notarized; missing: "
        + ", ".join(missing)
    )
    print(f"WARNING: {message}")
    # Also an annotation on the workflow run.
    if os.environ.get("GITHUB_ACTIONS") == "true":
        print(f"::warning::{message}")
    return False


def sign(identity=None):
    """Signs the app with the Developer ID identity, or with the given one
    ("-" for ad hoc)."""
    args = [
        "codesign",
        "--force",
        "--deep",
        "--options",
        "runtime",
        *([] if identity else getCodesignKeychainArgs()),
        "--sign",
        identity or getAppleCodesignIdentity(),
        "--digest-algorithm=sha1,sha256",
    ]
    if os.path.exists("build/Entitlements.plist"):
        args.extend(["--entitlements", "build/Entitlements.plist"])
    args.append(getBundlePath())
    run(args)


def notarize():
    bundleId = getPackageInformation().macos_bundle_id
    bundlePath = getBundlePath()
    bundleName = os.path.basename(bundlePath)
    bundleParentDir = os.path.dirname(bundlePath)
    if os.path.exists("build/_build/notarize.zip"):
        os.remove("build/_build/notarize.zip")
    # zip = "../../../notarize.zip"
    zip = "notarize.zip"
    shell(
        f'cd {bundleParentDir} && ditto -c -k --keepParent "{bundleName}" "{zip}"'
    )
    notarizeApp("build/_build/notarize.zip", bundleId)
    # if bundlePath.endswith(".framework"):
    #     print(
    #         "Does not seem to be possible to staple tickets to frameworks? (error 73)"
    #     )
    #     print("Exiting...")
    #     sys.exit(0)
    run(["xcrun", "stapler", "staple", bundlePath])


def archive_base_name():
    package = getPackageInformation()
    return f"{package.pretty_name}_{package.version}_{os_name}_{arch_name}"


def dist_archive_path():
    """The archive (or .dmg) that all() makes, in build/_dist."""
    if macos:
        extension = ".dmg"
    elif windows:
        extension = ".zip"
    else:
        extension = ".tar.xz"
    # With / also on Windows, for the workflow's shell.
    return f"build/_dist/{archive_base_name()}{extension}"


def archive():
    package = getPackageInformation()
    if windows:
        # archive_file = archive_base_name + ".zip"
        archive_format = "zip"
    elif macos:
        archive_format = ""
    else:
        archive_format = "xztar"

    if archive_format:
        archive = shutil.make_archive(
            os.path.join("build", "_dist", archive_base_name()),
            archive_format,
            os.path.join("build", "_build"),
            package.pretty_name,
        )
        print(archive)


def build_dmg():
    buildDmg()


def sign_dmg():
    signDmg()


def notarize_dmg():
    notarizeDmg()


def source():
    package = getPackageInformation()
    run(["make", "dist-xz", f"version={package.version}"])
    archive = f"{package.name}-{package.version}.tar.xz"
    if not os.path.exists("build/_dist"):
        os.makedirs("build/_dist")
    shutil.move(archive, "build/_dist")


def default():
    bootstrap()
    configure()
    build()
    bundle()


def all():
    signing = macos and macos_signing()
    bootstrap()
    configure()
    build()
    bundle()
    if macos:
        if signing:
            sign()
            notarize()
            build_dmg()
            sign_dmg()
            notarize_dmg()
        else:
            # Ad hoc, since the bundle was changed after PyInstaller signed
            # it (an arm64 app must be signed to run).
            sign(identity="-")
            build_dmg()
    else:
        archive()
    # For the dist workflow, which keeps the archive as an artifact.
    with open("build/_build/dist-archive.txt", "w") as f:
        f.write(dist_archive_path() + "\n")
    print(f"[BUILD] Made {dist_archive_path()}")


def main():
    args = sys.argv[1:]
    if len(args) == 0:
        args = ["default"]
    for arg in args:
        command = arg
        if command.startswith("--"):
            continue
        print("BUILD command:", command)
        if command == "all":
            all()
        elif command == "default":
            default()
        elif command == "version":
            version()
        elif command == "bootstrap":
            bootstrap()
        elif command == "configure":
            configure()
        elif command == "build":
            build()
        elif command == "bundle":
            bundle()
        elif command == "sign":
            sign()
        elif command == "notarize":
            notarize()
        elif command == "archive":
            archive()
        elif command == "build-dmg":
            build_dmg()
        elif command == "sign-dmg":
            sign_dmg()
        elif command == "notarize-dmg":
            notarize_dmg()
        elif command == "source":
            source()
        else:
            print(f"Unsupported command: {command}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
