import os
import shutil
import sys

from build.lib import (
    arch_name,
    macos,
    os_name,
    run,
    update_version_command,
    windows,
    # rmtree_if_exists,
    getPackageInformation,
    getAppleCodesignIdentity,
    getBundlePath,
    buildDmg,
    signDmg,
    notarizeApp,
    notarizeDmg,
    shell,
    upload
)


def version():
    update_version_command()


def bootstrap():
    run(["python", "./bootstrap"])


def configure():
    pass


def _remove_unwanted_pyqt_files(dir):
    for name in [
        # Linux
        "libgcc_s.so.1",
        "libQt6Pdf.so.6",
        "libQt6Svg.so.6",
        "libstdc++.so.6",
        "PyQt6/Qt6/lib/libQt6Pdf.so.6",
        "PyQt6/Qt6/lib/libQt6Svg.so.6",
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
    ]
    if windows or macos:
        args.append("--windowed")
    if macos:
        args.extend(
            ["--osx-bundle-identifier", "no.fengestad.fs-uae-launcher"]
        )
    args.append(script_name)
    run(args)
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
    <true/>
    <key>NSHighResolutionCapable</key>
    <true/>
  </dict>
</plist>
""")
        resources_dir = os.path.join(contents_dir, "Resources")
        shutil.copy("icon/fs-uae-launcher.icns",
                    os.path.join(resources_dir, "fs-uae-launcher.icns"))

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
            os.path.join("System", "Launcher", "Resources", item),
        )
        print(archive)


def sign():
    args = [
        "codesign",
        "--force",
        "--deep",
        "--options",
        "runtime",
        "--sign",
        getAppleCodesignIdentity(),
        "--digest-algorithm=sha1,sha256",
    ]
    if os.path.exists("build/Entitlements.plist"):
        args.extend(["--entitlements", "build/Entitlements.plist"])
    args.append(getBundlePath())
    run(args)
    # runCodeSign(args)


def notarize():
    bundleId = getPackageInformation().macos_bundle_id
    bundlePath = getBundlePath()
    bundleName = os.path.basename(bundlePath)
    bundleParentDir = os.path.dirname(bundlePath)
    if os.path.exists("build/_build/notarize.zip"):
        os.remove("build/_build/notarize.zip")
    zip = "../../../notarize.zip"
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


def archive():
    package = getPackageInformation()
    archive_base_name = (
        f"{package.pretty_name}_{package.version}_" + f"{os_name}_{arch_name}"
    )
    if windows:
        # archive_file = archive_base_name + ".zip"
        archive_format = "zip"
    elif macos:
        archive_format = ""
    else: 
        archive_format = "xztar"

    if archive_format:
        archive = shutil.make_archive(
            os.path.join("build", "_dist", archive_base_name),
            archive_format,
            os.path.join("build", "_build"),
            package.pretty_name
        )
        print(archive)


def build_dmg():
    buildDmg()


def sign_dmg():
    signDmg()


def notarize_dmg():
    notarizeDmg()


def default():
    bootstrap()
    configure()
    build()
    bundle()


def all():
    version()
    bootstrap()
    configure()
    build()
    bundle()
    if macos:
        sign()
        notarize()
        build_dmg()
        sign_dmg()
        notarize_dmg()
    else:
        archive()
    upload()


def main():
    args = sys.argv[1:]
    if len(args) == 0:
        args = ["default"]
    for arg in args:
        command = arg
        print("BUILD command:", command)
        if command == "all":
            all()
        if command == "default":
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
        elif command == "upload":
            upload()
        else:
            print(f"Unsupported command: {command}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
