import subprocess


def check_module(module_name):
    p = subprocess.Popen(["mypy", "-m", module_name], stderr=subprocess.PIPE)
    output = p.stderr.read()  # type: bytes
    if p.wait() != 0:
        print(output.decode("UTF-8"))
        raise Exception("mypy check failed for module {0}".format(module_name))
