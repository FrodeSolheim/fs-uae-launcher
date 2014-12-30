#!/usr/bin/env python3

import os
import sys
import shutil
import subprocess


# def fix_binary(path, frameworks_dir):
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

        old = line.split(' ')[0]
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
    frameworks_dir = os.path.join(app, "Contents", "Frameworks")
    extra_paths = []
    for name in os.listdir(macos_dir):
        p = os.path.join(macos_dir, name)
        if os.path.isdir(p):
            extra_paths.append(p)
        else:
            binaries.append(os.path.join(macos_dir, name))
    for extra_dir in extra_paths:
        for name in os.listdir(extra_dir):
            binaries.append(os.path.join(extra_dir, name))
    if os.path.exists(frameworks_dir):
        for name in os.listdir(frameworks_dir):
            binaries.append(os.path.join(frameworks_dir, name))
    changes = 0
    for binary in binaries:
        changes += fix_binary(binary, macos_dir)
    return changes


def main():
    app = sys.argv[1]
    while True:
        changes = fix_iteration(app)
        if changes == 0:
            break


if __name__ == "__main__":
    main()
