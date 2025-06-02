import os

from pkg_resources import resource_filename, resource_stream

from .application import Application


class Resources(object):
    def __init__(self, package, subdir=""):
        self.package = package
        self.subdir = subdir
        self.resource_sha1s = {}

    def resource_name(self, resource):
        if self.subdir:
            # return os.path.join(self.subdir, resource)
            return self.subdir + "/" + resource
        return resource

    def stream(self, resource):
        print("Resources.stream", resource)
        resource_name = self.resource_name(resource)
        # return resource_stream(self.package, str_path(resource_name))
        try:
            return resource_stream(self.package, resource_name)
        except Exception as e:
            print(e)
        try:
            return open(self.path(resource), "rb")
        except FileNotFoundError:
            raise LookupError(resource)

    def path(self, resource):
        application = Application.get_instance()
        resource_name = self.resource_name(resource)
        print("looking up resource", resource_name)
        print("- package:", self.package)

        relative_path = os.path.join(self.package, resource_name)
        try:
            return application.data_file(relative_path)
        except LookupError:
            pass

        try:
            # print("resource_filename(\"{0}\", \"{1}\")".format(
            #     self.package, resource_name))
            return resource_filename(self.package, resource_name)
            # return resource_filename(
            #     self.package, Paths.encode(resource_name))
        except Exception:
            pass

        raise LookupError("Cannot find resource {0}".format(repr(resource)))
