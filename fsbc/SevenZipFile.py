from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import sys
import subprocess
from distutils.spawn import find_executable
try:
    sevenzip_exe = find_executable(str("7z"))
except Exception:
    sevenzip_exe = None


class SevenZipFile:

    def __init__(self, path, mode="r"):
        if sevenzip_exe is None:
            raise Exception("no 7z executable found")

        assert mode == "r"
        self.path = path

        args = [sevenzip_exe, "l", "-slt", self.path]
        for i, arg in enumerate(args):
            args[i] = arg.encode(sys.getfilesystemencoding())
        print(args)
        p = subprocess.Popen(args, stdout=subprocess.PIPE)
        output = p.stdout.read()
        names = []
        last_name = None
        for line in output.split("\n"):
            name = line.strip().decode("UTF-8")
            print(name)
            if name.startswith("Path = "):
                last_name = name[7:]
                #names.append(name)
            elif name.startswith("Attributes = "):
                assert last_name
                if name.startswith("Attributes = D"):
                    names.append(last_name + "/")
                else:
                    names.append(last_name)
        # the first path is the name of the archive
        self.names = names[1:]
        # sort the name list so directory names are listed before contained
        # files
        self.names.sort()
        print(self.names)
        status = p.wait()
        if status != 0:
            raise Exception("7z status code not 0")

    def namelist(self):
        return self.names

    def read(self, name):
        args = [sevenzip_exe, "x", "-so", self.path, name]
        for i, arg in enumerate(args):
            args[i] = arg.encode(sys.getfilesystemencoding())
        print(args)
        p = subprocess.Popen(args, stdout=subprocess.PIPE)
        output = p.stdout.read()
        status = p.wait()
        if status != 0:
            raise Exception("7z status code not 0")
        return output

    def getinfo(self, name):
        if name in self.names:
            return {"name:": name}
        raise KeyError("{0} not found in archive".format(name))
