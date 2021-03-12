#!/usr/bin/env python3

import os
import sys
import shutil
import subprocess

nocopy_list = [
    "@rpath/QtCore.framework/Versions/5/QtCore",
    "@rpath/QtDBus.framework/Versions/5/QtDBus",
    "@rpath/QtGui.framework/Versions/5/QtGui",
    "@rpath/QtOpenGL.framework/Versions/5/QtOpenGL",
    "@rpath/QtPrintSupport.framework/Versions/5/QtPrintSupport",
    "@rpath/QtWidgets.framework/Versions/5/QtWidgets",
]


def fix_qt_frameworks(app):
    frameworks_dir = os.path.join(app, "Contents", "Frameworks")
    for framework in os.listdir(frameworks_dir):
        if not framework.startswith("Qt"):
            continue
        framework_dir = os.path.join(frameworks_dir, framework)
        print(framework)
        name, ext = framework.split(".")
        v5 = os.path.join(framework_dir, "Versions", "5")
        assert os.path.exists(v5)
        current = os.path.join(framework_dir, "Versions", "Current")
        if not os.path.exists(current):
            os.symlink("5", current)
        resources = os.path.join(v5, "Resources")
        if not os.path.exists(resources):
            os.makedirs(resources)
        # library_link = os.path.join(framework_dir, name)
        # if not os.path.exists(library_link):
        #     os.symlink(os.path.join("Versions", "Current", name), library_link)
        resources_link = os.path.join(framework_dir, "Resources")
        if not os.path.exists(resources_link):
            os.symlink("Versions/Current/Resources", resources_link)
        plist = os.path.join(resources, "Info.plist")
        with open(plist, "w", encoding="UTF-8") as f:
            f.write("""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
	<key>CFBundleExecutable</key>
	<string>{name}</string>
	<key>CFBundleGetInfoString</key>
	<string>Created by standalone.py</string>
	<key>CFBundleIdentifier</key>
	<string>org.qt-project.{name}</string>
	<key>CFBundlePackageType</key>
	<string>FMWK</string>
	<key>CFBundleShortVersionString</key>
	<string>1.0</string>
	<key>CFBundleSignature</key>
	<string>????</string>
	<key>CFBundleVersion</key>
	<string>1.0</string>
</dict>
</plist>
""".format(name=name))


def fix_binary(path, macos_dir):
    args = ["file", path] 
    p = subprocess.Popen(args, stdout=subprocess.PIPE)
    data = p.stdout.read().decode("UTF-8")
    p.wait()
    if "Mach-O" not in data:
        return 0

    print("fixing", path)
    changes = 0
    if not os.path.exists(path):
        raise Exception("could not find " + repr(path))

    args = ["otool", "-l", path] 
    p = subprocess.Popen(args, stdout=subprocess.PIPE)
    data = p.stdout.read().decode("UTF-8")
    p.wait()

    # Adding to rpath causes problems with signing
    # "because larger updated load commands do not fit"
    # if "@executable_path/../Frameworks" not in data:
    #     args = ["install_name_tool", "-add_rpath",
    #             "@executable_path/../Frameworks", path]
    #     print(args)
    #     p = subprocess.Popen(args)
    #     p.wait()

    # PyQt modules
    if "@loader_path/Qt/lib" in data:
        args = ["install_name_tool", "-rpath", "@loader_path/Qt/lib",
                "@executable_path/../Frameworks", path]
        print(args)
        p = subprocess.Popen(args)
        p.wait()
    # Qt frameworks
    if "@loader_path/../../lib" in data:
        args = ["install_name_tool", "-rpath", "@loader_path/../../lib",
                "@executable_path/../Frameworks", path]
        print(args)
        p = subprocess.Popen(args)
        p.wait()

    args = ["otool", "-L", path] 
    p = subprocess.Popen(args, stdout=subprocess.PIPE)
    data = p.stdout.read().decode("UTF-8")
    p.wait()
    for line in data.split('\n'):
        line = line.strip()
        if not line:
            continue
        if line.startswith("/usr/lib") or line.startswith("/System"):
            # old = line.split(' ')[0]
            # print("ignoring", old)
            continue
        if line.startswith("@executable_path"):
            continue

        old = line.split(" ")[0]
        # if old in ignore_list:
        #     continue
        if old == "@rpath/XCTest.framework/Versions/A/XCTest":
            continue
        if "Contents" in old:
            continue
        print(old)

        if os.path.basename(path) == os.path.basename(old):
            if "/" not in old:
                continue
            os.chmod(path, 0o755)
            args = ["install_name_tool", "-id", os.path.basename(path), path]
            print(args)
            p = subprocess.Popen(args)
            assert p.wait() == 0
            changes += 1
            continue

        # if not os.path.isabs(old):
        #     old = os.path.join(
        #         os.environ["DYLD_FALLBACK_LIBRARY_PATH"].split(":")[0], old)

        old_dir, name = os.path.split(old)
        # new = old.replace(old, '@executable_path/../Frameworks/' + name)
        new = old.replace(old, '@executable_path/' + name)
        # dst = os.path.join(frameworks_dir, os.path.basename(old))
        dst = os.path.join(macos_dir, os.path.basename(old))
        if not os.path.exists(dst):
            print("copying", old)
            libs_f.write(old + "\n")
            shutil.copy(old, dst)
            os.chmod(dst, 0o755)
            changes += 1
        # print(os.path.basename(path), "vs", os.path.basename(old))
        # if os.path.basename(path) == os.path.basename(old):
        #     args = ["install_name_tool", "-id", new, path]
        # else:
        os.chmod(path, 0o755)
        args = ["install_name_tool", "-change", old, new, path]
        print(args)
        p = subprocess.Popen(args)
        assert p.wait() == 0

    return changes


def fix_iteration(app):
    binaries = []
    macos_dir = os.path.join(app, "Contents", "MacOS")
    extra_paths = []
    for dir_path, dir_names, file_names in os.walk(macos_dir):
        for name in file_names:
            p = os.path.join(dir_path, name)
            if os.path.isdir(p):
                pass
            elif p.endswith("_debug.dylib"):
                pass
            else:
                binaries.append(p)
    # for name in os.listdir(macos_dir):
    #     p = os.path.join(macos_dir, name)
    #    if os.path.isdir(p):
    #         extra_paths.append(p)
    #     else:
    #         binaries.append(os.path.join(macos_dir, name))
    # for extra_dir in extra_paths:
    #     for name in os.listdir(extra_dir):
    #         p = os.path.join(extra_dir, name) 
    #         if os.path.isdir(p):
    #             for name2 in os.listdir(p):
    #                 if not name2.endswith("_debug.dylib"):
    #                     binaries.append(os.path.join(p, name2))
    #         else:
    #             binaries.append(p)

    frameworks_dir = os.path.join(app, "Contents", "Frameworks")
    if os.path.exists(frameworks_dir):
        for dir_path, dir_names, file_names in os.walk(frameworks_dir):
            for name in file_names:
                p = os.path.join(dir_path, name)
                binaries.append(p)

    # Qt plugins
    plugins_dir = os.path.join(app, "Contents", "PlugIns")
    if os.path.exists(plugins_dir):
        for dir_path, dir_names, file_names in os.walk(plugins_dir):
            for name in file_names:
                p = os.path.join(dir_path, name)
                binaries.append(p)

    changes = 0
    for binary in binaries:
        changes += fix_binary(binary, macos_dir)
    return changes


def main():
    global libs_f
    app = sys.argv[1]
    # fix_qt_frameworks(app)
    with open("libs.txt", "w") as libs_f:
        while True:
            changes = fix_iteration(app)
            if changes == 0:
                break


if __name__ == "__main__":
    main()
