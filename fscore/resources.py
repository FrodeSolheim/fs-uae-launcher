import os
from typing import IO

from pkg_resources import resource_filename, resource_stream
from fscore.applicationdata import ApplicationData

# from .application import Application


class Resources(object):
    def __init__(self, package: str, subdir: str = "data"):
        self.package = package
        self.subdir = subdir
        # self.resource_sha1s = {}

    def resource_name(self, name: str) -> str:
        if name.startswith("/"):
            # name has full path within package
            return name[1:]
        else:
            # name is relative to some subdir (possibly empty)
            if self.subdir:
                # return os.path.join(self.subdir, resource)
                return self.subdir + "/" + name
            return name

    def stream(self, name: str) -> IO[bytes]:
        print("Resources.stream", name)
        resource_name = self.resource_name(name)
        # return resource_stream(self.package, str_path(resource_name))
        try:
            return resource_stream(self.package, resource_name)
        except Exception as e:
            print(e)
        relative_path = os.path.join(self.package, resource_name)
        try:
            return ApplicationData.stream(relative_path)
        except FileNotFoundError:
            raise LookupError(name)

    def path(self, name: str) -> str:
        # application = Application.get_instance()
        resource_name = self.resource_name(name)
        print("looking up resource", resource_name)
        print("- package:", self.package)
        try:
            return resource_filename(self.package, resource_name)
        except Exception:
            pass

        relative_path = os.path.join(self.package, resource_name)
        try:
            return ApplicationData.path(relative_path)
        except LookupError:
            pass

        raise LookupError("Cannot find resource {0}".format(repr(name)))
