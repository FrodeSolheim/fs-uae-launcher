#!/usr/bin/env python3

import os
import sys
import subprocess

p = subprocess.Popen("file --dereference `which python3`",
                     shell=True, stdout=subprocess.PIPE)
exe_info = p.stdout.read().decode("UTF-8")
if "386," in exe_info:
    # arch = "i386"
    arch = "x86"
elif "x86-64," in exe_info:
    # arch = "amd64"
    arch = "x86-64"
else:
    raise Exception("unrecognized arch")

# if os.environ.get("STEAM_RUNTIME", ""):
if os.environ.get("STEAMOS", ""):
    os_name = "steamos"
    # if arch == "i386":
    #     # steam runtime sdk compiles with -mtune=generic -march=i686
    #     arch = "i686"
else:
    os_name = "linux"
    os_name_pretty = "Linux"

package_name = "fs-uae-launcher"
package_version = sys.argv[1]
dbg_package_dir = "{0}-dbg_{1}_{2}_{3}".format(
    package_name, package_version, os_name, arch)

package_dir = "../linux/Launcher/Linux//{}".format(arch)

full_package_name = "{0}_{1}_{2}_{3}".format(
    package_name, package_version, os_name, arch)
full_package_name_2 = "Launcher_{}_{}_{}".format(
    package_version, os_name_pretty, arch)


def s(command):
    c = command.format(**globals())
    print(c)
    assert os.system(c) == 0


def wrap(name, target=None, args=None):
    if target is None:
        target = name + ".bin"
        os.rename(os.path.join(package_dir, name),
                  os.path.join(package_dir, target))
    if args is None:
        args = ["$@"]
    path = os.path.join(package_dir, name)
    with open(path, "w") as f:
        f.write("#!/bin/sh\n")
        f.write("MYDIR=$(dirname \"$0\")\n")
        # f.write("export LD_LIBRARY_PATH=\"$MYDIR:$LD_LIBRARY_PATH\"\n")
        command = "\"$MYDIR/{0}\"".format(target)
        for arg in args:
            command += " \"{0}\"".format(arg)
        if os_name == "steamos":
            # if arch == "i686":
            if arch == "x86":
                bin_dir = "bin32"
            # elif arch == "amd64":
            elif arch == "x86-64":
                bin_dir = "bin32"
            else:
                raise Exception("unsupported steamos arch?")
            f.write("if [ -e \"$HOME/.steam/{0}/steam-runtime/"
                    "run.sh\" ]; then\n".format(bin_dir))
            f.write("RUN_SH=\"$HOME/.steam/{0}/steam-runtime/"
                    "run.sh\"\n".format(bin_dir))
            f.write("else\n")
            f.write("RUN_SH=\"/home/steam/.steam/{0}/steam-runtime/"
                    "run.sh\"\n".format(bin_dir))
            f.write("fi\n")
            f.write("exec $RUN_SH {0}\n".format(command))
        else:
            f.write("exec {0}\n".format(command))
    os.chmod(path, 0o755)


s("rm -Rf Launcher")
s("mkdir -p Launcher/Linux")
# s("make -C ..")
# s("rm -Rf ../build ../dist")

# Trying to get deterministic .pyc creation
s("cd ../.. && PYTHONHASHSEED=1 python3 setup.py build_exe")
s("mv ../../build/exe.linux-*-3.6 {package_dir}")

# we want to perform our own standalone/library management, so we remove the
# libraries added by cx_Freeze
s("rm -f {package_dir}/*.so.*")
s("rm -f {package_dir}/imageformats/*.so.*")

s("rm -f {package_dir}/platforms/libqdirectfb.so")
s("rm -f {package_dir}/platforms/libqlinuxfb.so")
s("rm -f {package_dir}/platforms/libqminimal.so")
s("rm -f {package_dir}/platforms/libqoffscreen.so")
s("./standalone-linux.py {package_dir}/platforms")
s("mv {package_dir}/platforms/*.so.* {package_dir}")
s("./standalone-linux.py --no-copy --strip --rpath='$ORIGIN/..' {package_dir}/platforms")
# s("rm {package_dir}/platforms/*.so.*")

s("rm -f {package_dir}/imageformats/libqdds.so")
s("rm -f {package_dir}/imageformats/libqicns.so")
s("rm -f {package_dir}/imageformats/libqjp2.so")
s("rm -f {package_dir}/imageformats/libqmng.so")
s("rm -f {package_dir}/imageformats/libqsvg.so")
s("rm -f {package_dir}/imageformats/libqtga.so")
s("rm -f {package_dir}/imageformats/libqtiff.so")
s("rm -f {package_dir}/imageformats/libqwbmp.so")
s("rm -f {package_dir}/imageformats/libqwebp.so")
s("./standalone-linux.py {package_dir}/imageformats")
s("mv {package_dir}/imageformats/*.so.* {package_dir}")
s("./standalone-linux.py --no-copy --strip --rpath='$ORIGIN/..' {package_dir}/imageformats")
# s("rm {package_dir}/imageformats/*.so.*")

from PyQt5 import QtCore
dir0 = os.path.join(os.path.dirname(QtCore.__file__), "plugins")
for libpath in QtCore.QCoreApplication.libraryPaths() + [dir0]:
    print(libpath)
    p = os.path.join(libpath, "xcbglintegrations")
    if os.path.exists(p):
        s("cp -a \"{0}\" {{package_dir}}/".format(p))
s("./standalone-linux.py {package_dir}/xcbglintegrations")
s("mv {package_dir}/xcbglintegrations/*.so.* {package_dir}")
s("./standalone-linux.py --no-copy --strip --rpath='$ORIGIN/..' {package_dir}/xcbglintegrations")
# s("rm {package_dir}/xcbglintegrations/*.so.*")

# s("mv {package_dir}/platforms/* {package_dir}")
# s("mv {package_dir}/imageformats/* {package_dir}")
# s("mv {package_dir}/xcbglintegrations/* {package_dir}")
# s("rm -Rf {package_dir}/platforms")
# s("rm -Rf {package_dir}/imageformats")
# s("rm -Rf {package_dir}/xcbglintegrations")

# s("./standalone-linux.py {package_dir}")
# s("strip {package_dir}/*.so.*")
# s("strip {package_dir}/*.so")

# Must remove .standalone files to force processing the ones copied
# from the Qt plugin dirs
s("find {package_dir} -name '*.standalone' -delete")
s("./standalone-linux.py --strip --rpath='$ORIGIN' {package_dir}")
s("find {package_dir} -name '*.standalone' -delete")

s("chmod a-x {package_dir}/*.so")
s("cd ../.. && make")
s("mkdir Launcher/Data")
s("cp ../../cacert.pem Launcher/Data")
s("cp -a ../../share/locale Launcher/Data/Locale")
# s("cp -a ../../share {package_dir}")
# s("rm -Rf {package_dir}/share/applications")
# s("rm -Rf {package_dir}/share/icons")

s("rm -Rf {package_dir}/amitools")
s("rm -Rf {package_dir}/arcade")
s("rm -Rf {package_dir}/fsbc")
# s("rm -Rf {package_dir}/fsboot")
s("rm -Rf {package_dir}/fsgs")
s("rm -Rf {package_dir}/fspy")
s("rm -Rf {package_dir}/fstd")
s("rm -Rf {package_dir}/fsui")
s("rm -Rf {package_dir}/launcher")
s("rm -Rf {package_dir}/OpenGL")
s("rm -Rf {package_dir}/oyoyo")
s("rm -Rf {package_dir}/workspace")

s("zip -d {package_dir}/library.zip amitools/\*")
s("zip -d {package_dir}/library.zip arcade/\*")
s("zip -d {package_dir}/library.zip fsbc/\*")
# s("zip -d {package_dir}/library.zip fsboot/\*")
s("zip -d {package_dir}/library.zip fsgs/\*")
s("zip -d {package_dir}/library.zip fspy/\*")
s("zip -d {package_dir}/library.zip fstd/\*")
s("zip -d {package_dir}/library.zip fsui/\*")
s("zip -d {package_dir}/library.zip launcher/\*")
s("zip -d {package_dir}/library.zip OpenGL/\*")
s("zip -d {package_dir}/library.zip oyoyo/\*")
s("zip -d {package_dir}/library.zip workspace/\*")

s("zip -d {package_dir}/library.zip BUILD_CONSTANTS.pyc")
s("PYTHONPATH=../.. python3 -m fspy.zipfile deterministic "
  "--fix-pyc-timestamps {package_dir}/library.zip")

# s("cp -a ../python/*.zip {package_dir}")
s("mkdir Launcher/Python")
s("cp -a ../python/*.zip Launcher/Python")

s("echo {package_version} > Launcher/Version.txt")
s("echo {package_version} > {package_dir}/Version.txt")

if os_name == "steamos":
    # s("mv {package_dir}/fs-uae-launcher {package_dir}/fs-uae-launcher.bin")
    wrap("fs-uae-launcher")
    wrap("fs-uae-arcade", "fs-uae-launcher.bin", ["--fs-uae-arcade", "$@"])

# s("cd {package_dir} && tar Jcfv ../../../{full_package_name}.tar.xz *")
s("tar Jcfv ../../{full_package_name}.tar.xz Launcher")
s("cp ../../{full_package_name}.tar.xz ../../{full_package_name_2}.tar.xz")

# s("rm -Rf {dbg_package_dir}")
# s("mkdir {dbg_package_dir}")
# s("cp -a ../fs-uae.dbg {dbg_package_dir}/")
# s("cp -a ../fs-uae-device-helper.dbg {dbg_package_dir}/")
# s("cd {dbg_package_dir} && tar Jcfv ../../{dbg_package_dir}.tar.xz *")
