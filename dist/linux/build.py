#!/usr/bin/env python3

import os
import sys
import subprocess

p = subprocess.Popen("file --dereference `which python3`",
                     shell=True, stdout=subprocess.PIPE)
exe_info = p.stdout.read().decode("UTF-8")
if "386" in exe_info:
    # arch = "i386"
    arch = "x86"
elif "x86-64" in exe_info:
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

package_name = "fs-uae-launcher"
package_version = sys.argv[1]
dbg_package_dir = "{0}-dbg_{1}_{2}_{3}".format(
    package_name, package_version, os_name, arch)
package_dir = "../{2}/{0}_{1}_{2}_{3}".format(
    package_name, package_version, os_name, arch)
full_package_name = "{0}_{1}_{2}_{3}".format(
    package_name, package_version, os_name, arch)


def s(command):
    c = command.format(**globals())
    print(c)
    assert os.system(c) == 0


def wrap(name, target, args=None):
    if args is None:
        args = ["$@"]
    path = os.path.join(package_dir, name)
    with open(path, "w") as f:
        f.write("#!/bin/sh\n")
        f.write("MYDIR=$(dirname \"$0\")\n")
        f.write("export LD_LIBRARY_PATH=\"$MYDIR:$LD_LIBRARY_PATH\"\n")
        command = "\"$MYDIR/{0}\"".format(target)
        for arg in args:
            command += " \"{0}\"".format(arg)
        if os_name == "steamos":
            # if arch == "i686":
            if arch == "x86":
                bin_dir = "bin32"
            # elif arch == "amd64":
            elif arch == "x86-64":
                bin_dir = "bin64"
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


s("rm -Rf {package_dir}")
# s("make -C ..")
# s("rm -Rf ../build ../dist")
s("cd ../.. && python3 setup.py build_exe")
s("mv ../../build/exe.linux-*-3.4 {package_dir}")

# we want to perform our own standalone/library management, so we remove the
# libraries added by cx_Freeze
s("rm -f {package_dir}/*.so.*")
s("rm -f {package_dir}/imageformats/*.so.*")

s("./standalone.py {package_dir}/platforms")
s("mv {package_dir}/platforms/*.so.* {package_dir}")
s("./standalone.py {package_dir}/imageformats")
s("mv {package_dir}/imageformats/*.so.* {package_dir}")
s("./standalone.py {package_dir}")
s("strip {package_dir}/*.so.*")
s("strip {package_dir}/*.so")
s("strip {package_dir}/imageformats/*.so")
s("chmod a-x {package_dir}/*.so")
s("cd ../.. && make")
s("cp -a ../../share {package_dir}")

s("mv {package_dir}/fs-uae-launcher {package_dir}/fs-uae-launcher.bin")
wrap("fs-uae-launcher", "fs-uae-launcher.bin")
wrap("fs-uae-arcade", "fs-uae-launcher.bin", ["--fs-uae-arcade", "$@"])

s("cd {package_dir} && tar Jcfv ../../../{full_package_name}.tar.xz *")

# s("rm -Rf {dbg_package_dir}")
# s("mkdir {dbg_package_dir}")
# s("cp -a ../fs-uae.dbg {dbg_package_dir}/")
# s("cp -a ../fs-uae-device-helper.dbg {dbg_package_dir}/")
# s("cd {dbg_package_dir} && tar Jcfv ../../{dbg_package_dir}.tar.xz *")
