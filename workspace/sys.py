import logging
import os
import sys

import subprocess

import workspace.path
from fsgs.plugins.pluginmanager import PluginManager

logger = logging.getLogger("SYS")


def program_path():
    return [
        "SYS:C",
        "SYS:Utilities",
        "SYS:Rexxc",
        "SYS:System",
        "SYS:S",
        "SYS:Prefs",
        "SYS:WSStartup",
        "SYS:Tools",
        "SYS:Tools/Commodities",
    ]


def rexx_path():
    return ["SYS:S"]


def find_program(program):
    program = program.lower()
    for dir in program_path():
        try:
            for item in workspace.path.listdir(dir):
                if item.lower() == program:
                    p = workspace.path.join(dir, item, item + ".py")
                    if workspace.path.exists(p):
                        return workspace.path.join(dir, item)
        except FileNotFoundError:
            continue
    raise FileNotFoundError("Could not find program " + repr(program))


def workspace_exec(args):
    logger.debug("shell_exec %s", repr(args))
    program_name = args[0]
    program = find_program(program_name)
    logger.debug("%s", repr(program))

    module = load_python_program_module(program)

    if hasattr(module, "workspace_exec"):
        # print("running module.workspace_exec", module)
        return module.workspace_exec(args)

    # FIXME: other exception
    raise FileNotFoundError("Cannot exec")
    # if hasattr(module, "shell_open"):
    #     module.shell_open(args)
    # else:
    #     module.open()


def load_python_program_module(path):
    logger.debug("load_python_program_module %s", repr(path))
    # FIXME: Not nice, requires globally unique module names for apps.
    import importlib

    host_path = workspace.path.host(
        workspace.path.join(path, workspace.path.basename(path) + ".py")
    )
    host_dir = os.path.dirname(host_path)
    if host_dir not in sys.path:
        sys.path.insert(0, host_dir)
    module = importlib.import_module(
        os.path.splitext(os.path.basename(host_path))[0]
    )
    logger.debug("%s", repr(module))
    return module


def python_exec(script, argv):
    env = os.environ.copy()
    env["PYTHONPATH"] = ":".join(sys.path)
    p = subprocess.Popen(
        [sys.executable, script] + argv[1:],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        env=env,
        stderr=subprocess.STDOUT,
        bufsize=0,
    )
    return p


def expansion_exec(exe_name, argv):
    executable = PluginManager.instance().find_executable(exe_name)
    p = executable.popen(
        argv[1:],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        bufsize=0,
    )
    return p


def host_exec(exe, argv):
    print([exe] + argv[1:])
    p = subprocess.Popen(
        [exe] + argv[1:],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        bufsize=0,
    )
    return p
