import logging

from pkg_resources import resource_stream

from fscore.resources import Resources as BaseResources
from fsui.qt import QImage

logger = logging.getLogger("arcade")


def _(msg: str) -> str:
    return str(msg)


# FIXME: Incorrect argument order
def ngettext(n, msg1, msg2):
    return str(msg1) if n == 1 else str(msg2)


class Resources(BaseResources):
    def __init__(self, package: str):
        BaseResources.__init__(self, package, "data")
        self.req = package

    def resource_pil_image(self, resource: str):
        # resource_name = encode_path(u'res/' + resource_name)
        # return resource_pil_image(self.req, resource_name)
        stream = self.stream(resource)
        # noinspection PyUnresolvedReferences
        from PIL import Image

        return Image.open(stream)

    def resource_qt_image(self, resource: str) -> QImage:
        stream = self.stream(resource)
        im = QImage()
        im.loadFromData(stream.read())
        return im

    def resource_stream(self, resource: str):
        return self.stream(resource)

    def resource_filename(self, resource: str):
        return self.path(resource)


def resource_pil_image(package_or_requirement: str, resource_name: str):
    # print("resource_pil_image", package_or_requirement, resource_name)
    stream = resource_stream(package_or_requirement, resource_name)
    # noinspection PyUnresolvedReferences
    from PIL import Image

    return Image.open(stream)


# def resource_icon_stream(package_or_requirement, name, size):
#     #print(name, size)
#     resource_name = encode_path(u'res/icons/%dx%d/%s.png' % (size, size,
# name))
#     return resource_stream(package_or_requirement, resource_name)


# def resource_icon_pil(package_or_requirement, name, size):
#     #print("resource_icon_pil", name, size)
#     #path = os.path.join(self.path, "icons",
#     #        "%dx%d" % (size, size), name + ".png")
#     #if os.path.isfile(path):
#     #    return Image.open(path)
#     stream = resource_icon_stream(package_or_requirement, name, size)
#     from PIL import Image
#     return Image.open(stream)

gettext = _

resources = Resources("arcade")
