import os
import sys
if sys.argv[1] == "build_exe":
    from cx_Freeze import setup, Executable
else:
    from distutils.core import setup

if "install" in sys.argv:
    for arg in sys.argv:
        if arg.startswith("--install-lib="):
            break
    else:
        print("ERROR: You should not install FS-UAE Launcher to the default ")
        print("python library location. Instead, use --install-lib to ")
        print("install to a custom location, e.g.:")
        print("python3 setup.py --install-lib=/usr/share/fs-uae-launcher install")
        sys.exit(1)

title = "FS-UAE Launcher"
name = "fs-uae-launcher"
py_name = "fs_uae_launcher"
tar_name = "fs-uae-launcher"
version = "3.2.20"
author = "Frode Solheim"
author_email = "frode@fs-uae.net"
package_map = {
    "amitools": ".",
    "arcade": ".",
    "fsbc": ".",
    "fsboot": ".",
    "fsgs": ".",
    "fspy": ".",
    "fstd": ".",
    "fsui": ".",
    "launcher": ".",
    "oyoyo": ".",
    "workspace": ".",
}
packages = sorted(package_map.keys())
scripts = ["fs-uae-launcher"]


# add unique parent directories to sys.path
for p in set(package_map.values()):
    sys.path.insert(0, p)

setup_packages = set()
package_dir = {}
package_data = {}
setup_options = {}
setup_cmdclass = {}


res_dirs = []
res_dirs.append('amitools/res')
res_dirs.append('arcade/res')
res_dirs.append('fsbc/res')
res_dirs.append('fsboot/res')
res_dirs.append('fsgs/res')
res_dirs.append('fspy/res')
res_dirs.append('fstd/res')
res_dirs.append('fsui/res')
res_dirs.append('launcher/res')
res_dirs.append('oyoyo/res')
res_dirs.append('workspace/res')


def add_package(package_name, package_dir_name):
    setup_packages.add(package_name)
    local_name = package_name.replace(".", "/")
    if os.path.exists(local_name):
        package_dir_path = local_name
    else:
        package_dir_path = package_dir_name + "/" + local_name
    package_dir[package_name] = package_dir_path
    package_data[package_name] = []
    for dir_path, dir_names, file_names in os.walk(package_dir_path):
        for name in file_names:
            n, ext = os.path.splitext(name)
            if ext in [".py", ".pyc", ".pyo", ".swp", "*.swo"]:
                continue
            path = os.path.join(dir_path[len(package_dir_path) + 1:], name)
            package_data[package_name].append(path)
            setup_packages.add(package_name)


def add_packages():
    for name in sorted(packages):
        dir_name = package_map[name]
        add_package(name, dir_name)
        for dir_path, dir_names, file_names in os.walk(
                package_dir[name]):
            for n in file_names:
                if n != "__init__.py":
                    continue
                p_name_rev = []
                path = dir_path
                while os.path.exists(os.path.join(path, "__init__.py")):
                    p_name_rev.append(os.path.basename(path))
                    path = os.path.dirname(path)
                sub_name = ".".join(reversed(p_name_rev))
                package_dir[sub_name] = (package_dir[name] + "/" +
                                         sub_name.replace(".", "/"))
                add_package(sub_name, dir_name)


add_packages()

setup_kwargs = {
    "name": py_name,
    "version": version,
    "author": author,
    "author_email": author_email,
    "packages": setup_packages,
    "package_dir": package_dir,
    "package_data": package_data,
    "options": setup_options,
    "cmdclass": setup_cmdclass,
}

if sys.argv[1] == "build_exe":
    import cx_Freeze
    if sys.platform == "win32":
        setup_kwargs["executables"] = [
            Executable(s, base="Win32GUI", icon="icon/" + s + ".ico")
                for s in scripts]
    else:
        setup_kwargs["executables"] = [Executable(s) for s in scripts]

    setup_kwargs["version"] = "3.2.20"
    build_exe_options = {
        "includes": [
        #    "ctypes",
        #    "logging",
        ],
        "excludes": [
            "tkconstants",
            "tkinter",
            "tk",
            "tcl",
        ],
        "include_files": [],
        "zip_includes": [],
    }
    if int(cx_Freeze.version.split(".")[0]) >= 5:
        build_exe_options["zip_include_packages"] = "*"
        build_exe_options["zip_exclude_packages"] = []
    #for res_dir in res_dirs:
    #    print(res_dir)
    #    build_exe_options["zip_includes"].append((res_dir, res_dir))

    for name in sorted(package_map.keys()):
        sp = os.path.join(name, "res")
        if not os.path.exists(sp):
            # setup with alternative source dir
            sp = os.path.join(package_map[name], name, "res")
        if not os.path.exists(sp):
            continue
        dp = os.path.join(name, "res")
        # dp = os.path.join("share", tar_name, dp)
        # build_exe_options["include_files"].append((sp, dp))
        for dir_path, dir_names, file_names in os.walk(sp):
            for name in file_names:
                p = os.path.join(dir_path, name)
                rp = p[len(sp) + 1:]
                # build_exe_options["zip_includes"].append(
                #     (p, os.path.join(dp, rp)))
                build_exe_options["include_files"].append(
                    (p, os.path.join(dp, rp)))
                # print(p, rp)
    setup_options["build_exe"] = build_exe_options
    if os.path.exists("extra_imports.py"):
        build_exe_options["includes"].append("extra_imports")

    build_exe_options["packages"] = setup_packages


if sys.platform == "win32" and False:
    setup_kwargs["windows"] = scripts

if sys.platform == "darwin":
    setup_kwargs["name"] = title
    setup_kwargs["version"] = "3.2.20"
else:
    setup_kwargs["scripts"] = scripts

setup(**setup_kwargs)
