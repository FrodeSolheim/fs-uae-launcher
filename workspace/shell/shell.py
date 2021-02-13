import builtins
import os
import subprocess
import sys
import zipfile

import workspace.path
import workspace.ui

STATE_NORMAL = 0
STATE_SELECTED = 1


def workspace_open(path, args=None):
    if args is None:
        args = []
    print("workspace.shell.open", path)
    t = tool(path)
    print(t)
    if not t:
        t = default_tool(path)
    if t:
        args.insert(0, path)
        return open(t, args)
    else:
        name = workspace.path.basename(path)
        app_path = workspace.path.join(path, name + ".py")
        print("APP PATH", app_path)
        if workspace.path.exists(app_path):
            print("Exists!")
            return open_app(app_path, args)

    print("open", path, args)

    if path in ["C:Python", "Python"]:
        print(sys.executable)
        p = subprocess.Popen([sys.executable, "run.py", "Python"] + args)
    elif path in ["C:FS-UAE", "FS-UAE", "SYS:System/FS-UAE"]:
        # FIXME: Spawn via "FS-UAE Launcher" instead, respecting Launcher
        # settings, etc.
        from fsgamesys.amiga.fsuae import FSUAE

        # FIXME: Other args
        FSUAE.start_with_args([workspace.path.host(args[0])])


# FIXME:
open = workspace_open


def open_app(path, args=None):
    print("open_app", path, args)
    # FIXME: Use sys load_python_program_module
    # FIXME: Not a nice method, requires globally unique module names for
    # applications
    import importlib

    host_path = workspace.path.host(path)
    host_dir = os.path.dirname(host_path)
    if host_dir not in sys.path:
        sys.path.insert(0, host_dir)
    module = importlib.import_module(
        os.path.splitext(os.path.basename(host_path))[0]
    )
    print(module.__file__)
    if hasattr(module, "workspace_open"):
        module.workspace_open(args)
    elif hasattr(module, "shell_open"):
        module.shell_open(args)
    else:
        module.open()


def file_type_icon(file_type, state=STATE_NORMAL):
    print("get file type icon for", file_type)
    icon_name = "icon.png"
    if state:
        icon_name = "selected.png"
    try:
        return icon_from_zip(
            "SYS:Icons/FileTypes/{}.fs-info".format(file_type), icon_name
        )
    except LookupError:
        pass
    p = "SYS:Icons/FileTypes/{}.fs-info/{}".format(file_type, icon_name)
    print(p)
    if workspace.path.exists(p):
        return workspace.ui.Image(p)
    return None


def default_icon(path, state=STATE_NORMAL):
    print("get default icon for", path)
    ext = workspace.path.extension(path, prefix=True, suffix=True)
    print(ext)
    return file_type_icon(ext, state)

    # try:
    #     return icon_from_zip(
    #         "SYS:Icons/FileTypes/{}.fs-info".format(ext), icon_name)
    # except LookupError:
    #     pass
    # p = "SYS:Icons/FileTypes/{}.fs-info/{}".format(ext, icon_name)
    # print(p)
    # if workspace.path.exists(p):
    #     return workspace.ui.Image(p)
    # return None


def stream_from_zip(path, name):
    try:
        zf = zipfile.ZipFile(workspace.path.host(path))
        return zf.open(name, "r")
    except (FileNotFoundError, IsADirectoryError, KeyError):
        raise LookupError(name)


def icon_from_zip(path, icon_name):
    return workspace.ui.Image(stream_from_zip(path, icon_name))


def icon(path, state=STATE_NORMAL):
    icon_name = "icon.png"
    if state:
        icon_name = "selected.png"
    try:
        return icon_from_zip(path + ".fs-info", icon_name)
    except LookupError:
        try:
            return icon_from_zip(os.path.join(path, ".fs-info"), icon_name)
        except (LookupError, NotADirectoryError):
            pass

    # p = workspace.path.host(
    p = workspace.path.join(path + ".fs-info", icon_name)
    print(p, os.path.exists(p))
    if not workspace.path.exists(p):
        # p = workspace.path.host(
        p = workspace.path.join(path, ".fs-info", icon_name)
        print(p, os.path.exists(p))
    if workspace.path.exists(p):
        return workspace.ui.Image(p)
    # return default_icon(path, state=state)
    return None


def default_tool(path):
    ext = workspace.path.extension(path, prefix=True, suffix=True)
    if ext in ["txt", "ini", "inf", "html"]:
        return "SYS:Utilities/MultiView"
    elif ext in ["url"]:
        return "SYS:System/WebBrowser"
    elif ext in ["fs-uae"]:
        return "SYS:System/FS-UAE"
    elif ext in ["mod"]:
        return "SYS:Utilities/ModulePlayer"
    # if ext == "fs-uae":
    #     return "FS-UAE"
    # if ext == "html":
    #     return "HTMLView"
    # if ext == "py":
    #     return "Python"
    # if ext == "mod":
    #     return "ModulePlayer"
    # if ext == "url":
    #     return "WebBrowser"
    # if ext == "adf":
    #     return "FS-UAE"
    return None


def tool(path):
    p = workspace.path.host(workspace.path.join(path + ".fs-info", "tool.txt"))
    print(p, os.path.exists(p))
    if not os.path.exists(p):
        p = workspace.path.host(
            workspace.path.join(path, ".fs-info", "tool.txt")
        )
        print(p, os.path.exists(p))
    if os.path.exists(p):
        with builtins.open(p, "r", encoding="UTF-8") as f:
            text = f.read().strip()
            return text
    return None
