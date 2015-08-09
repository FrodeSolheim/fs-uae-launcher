import os
from pkg_resources import resource_filename
from .Application import Application


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
        # resource_name = self.resource_name(resource)
        # return resource_stream(self.package, str_path(resource_name))
        # try:
        #     return resource_stream(self.package, Paths.encode(resource_name))
        # except Exception:
        #     return open(self.path(resource), "rb")
        try:
            return open(self.path(resource), "rb")
        except FileNotFoundError:
            raise LookupError(resource)

    def path(self, resource):
        print("looking up resource", resource)
        print("- package:", self.package)
        application = Application.get_instance()
        resource_name = self.resource_name(resource)
        print("resource_name", resource_name)

        relative_path = os.path.join(self.package, resource_name)
        try:
            return application.data_file(relative_path)
        except LookupError:
            pass

        try:
            print("resource_filename(\"{0}\", \"{1}\")".format(
                self.package, resource_name))
            return resource_filename(self.package, resource_name)
            # return resource_filename(
            #     self.package, Paths.encode(resource_name))
        except Exception:
            pass

        raise LookupError(
            "Cannot find resource {0}".format(repr(resource)))

        # try:
        #     sha1 = self.resource_sha1s[resource]
        # except KeyError:
        #     stream = self.stream(resource)
        #     data = stream.read()
        #     sha1 = hashlib.sha1(data).hexdigest()
        #     self.resource_sha1s[resource] = sha1
        # else:
        #     data = None

        # _, ext = os.path.splitext(resource)
        # ext = ext or ".bin"
        # cache_path = os.path.join(application.cache_dir(), "Temp", sha1 + ext)
        # if not os.path.exists(cache_path):
        #     if not os.path.exists(os.path.dirname(cache_path)):
        #         os.makedirs(os.path.dirname(cache_path))
        #     if data is None:
        #         stream = self.stream(resource)
        #         data = stream.read()
        #     with open(cache_path + ".partial", "wb") as f:
        #         f.write(data)
        #     os.rename(cache_path + ".partial", cache_path)
        # return cache_path

        # if not path or not os.path.exists(path):
        #     raise LookupError(
        #         "Cannot find resource {0}".format(repr(resource)))
        # return path


# import os
# import sys
# import logging
# from fengestad.fs import encode_path, memoize
#
# logger = logging.getLogger('fengestad.game_center')
#
# def _(msg):
#     return six.text_type(msg)
#
# def ngettext(n, msg1, msg2):
#     return six.text_type(msg1) if n == 1 else six.text_type(msg2)
#
# class Resources(object):
#     def __init__(self, package_or_requirement):
#         self.req = package_or_requirement
#
#     def resource_pil_image(self, resource_name):
#         resource_name = encode_path(u'res/' + resource_name)
#         return resource_pil_image(self.req, resource_name)
#
#     def resource_stream(self, resource_name):
#         resource_name = encode_path(u'res/' + resource_name)
#         return resource_stream(self.req, resource_name)
#
#     def resource_filename(self, resource_name):
#         print >> sys.stderr, resource_name
#         try:
#             resource_name_2 = encode_path(u'res/' + resource_name)
#             path = resource_filename(self.req, resource_name_2)
#             print >> sys.stderr, path
#             if not os.path.exists(path):
#                 raise Exception("Cannot find resource {0}".format(
#                         repr(resource_name)))
#             return path
#         except Exception:
#             # for Windows
#             path = os.path.join("share", "fs-game-center", resource_name)
#             print >> sys.stderr, os.getcwd()
#             print >> sys.stderr, path
#             if os.path.exists(path):
#                 return path
#             raise Exception(
#                 "Cannot find resource {0}".format(repr(resource_name)))

# def resource_pil_image(package_or_requirement, resource_name):
#     #print("resource_pil_image", package_or_requirement, resource_name)
#     stream = resource_stream(package_or_requirement, resource_name)
#     #from PIL import Image
#     import Image
#     return Image.open(stream)
#
#
# def resource_icon_stream(package_or_requirement, name, size):
#     #print(name, size)
#     resource_name = encode_path(u'res/icons/%dx%d/%s.png' % (
#         size, size, name))
#     return resource_stream(package_or_requirement, resource_name)
#
#
# def resource_icon_pil(package_or_requirement, name, size):
#     #print("resource_icon_pil", name, size)
#     #path = os.path.join(self.path, "icons",
#     #        "%dx%d" % (size, size), name + ".png")
#     #if os.path.isfile(path):
#     #    return Image.open(path)
#     stream = resource_icon_stream(package_or_requirement, name, size)
#     #from PIL import Image
#     import Image
#     return Image.open(stream)
#
#
# resources = Resources("fengestad.game_center")
