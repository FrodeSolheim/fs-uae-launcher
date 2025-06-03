import os
import zipfile

from .application import Application


class Resources(object):
    zip_files = {}

    @classmethod
    def resource_zip(cls, package: str):
        application = Application.get_instance()
        try:
            file = application.data_file(f"{package}.zip")
        except LookupError:
            file = None
        if package not in cls.zip_files:
            if file is None:
                cls.zip_files[package] = None
            else:
                zip_file = zipfile.ZipFile(file)
                cls.zip_files[package] = zip_file
        return cls.zip_files[package]

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
        print("Resources.stream", self.package, resource)
        zip = self.resource_zip(self.package)
        if zip is not None:
            print("Resources zip.open", zip, resource)
            try:
                return zip.open(resource)
            except KeyError:
                pass

        try:
            return open(self.path(resource), "rb")
        except FileNotFoundError:
            raise LookupError(resource)

    def path(self, resource):
        application = Application.get_instance()
        resource_name = self.resource_name(resource)
        print("looking up resource", resource_name, "package =", self.package)

        relative_path = os.path.join(self.package, resource_name)
        try:
            return application.data_file(relative_path)
        except LookupError:
            pass

        raise LookupError("Cannot find resource {0}".format(repr(resource)))
